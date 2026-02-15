"""ELIMS Backend - MQTT Subscriber Module."""

import json
from collections.abc import Callable
from datetime import UTC, datetime
from queue import Empty as QueueEmpty
from queue import Queue
from threading import Event, Thread

from app.api.temperature.models import Temperature
from app.config import settings
from elims_common.logger.logger import logger
from elims_common.mqtt import MQTTConfig
from elims_common.mqtt import MQTTSubscriber as BaseMQTTSubscriber
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

CLIENT_TYPE = "subscriber"
CLIENT_ID = f"elims-backend-{CLIENT_TYPE}"
MQTT_BACKEND_CONFIG = MQTTConfig(
    broker_host=settings.mqtt_host,
    broker_port=settings.mqtt_port,
    client_id=CLIENT_ID,
    client_type=CLIENT_TYPE,
    username=settings.mqtt_username,
    password=SecretStr(settings.mqtt_password),
    lwt_topic=f"elims/{CLIENT_ID}/status",
    lwt_payload=json.dumps({"status": "offline"}),
    keepalive=60,
    reconnect_on_failure=True,
    certificate_authority_file=settings.mqtt_certificate_authority_file,
    certificate_file=settings.mqtt_certificate_file,
    key_file=settings.mqtt_key_file,
    tls_insecure=settings.mqtt_tls_insecure,
)

# Create synchronous engine for subscriber thread (avoids async/await issues)
sync_db_url = settings.db_url
if sync_db_url.startswith("mysql+aiomysql://"):
    sync_db_url = sync_db_url.replace("mysql+aiomysql://", "mysql+pymysql://")
elif sync_db_url.startswith("mysql://"):
    sync_db_url = sync_db_url.replace("mysql://", "mysql+pymysql://")

sync_engine = create_engine(sync_db_url, echo=settings.sql_echo)


class MQTTSubscriber(BaseMQTTSubscriber):
    """Custom MQTT Subscriber for ELIMS."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize subscriber with environment defaults."""
        super().__init__(config)
        self.queue: Queue[dict] = Queue()

    def subscribe_raspberry_telemetry(self, callback: Callable[[str, dict[str, object]], None]) -> None:
        """Subscribe to raspberry telemetry topics with JSON parsing."""

        def wrapper(topic: str, payload: str) -> None:
            try:
                data = json.loads(payload)
                callback(topic, data)
            except json.JSONDecodeError:
                logger.error(self.msg.invalid_json_payload(topic, payload))

        self.subscribe("devices/+/telemetry", wrapper)

    def subscribe_raspberry_system(self, callback: Callable[[str, dict[str, object]], None]) -> None:
        """Subscribe to raspberry system status updates with JSON parsing."""

        def wrapper(topic: str, payload: str) -> None:
            try:
                data = json.loads(payload)
                callback(topic, data)
            except json.JSONDecodeError:
                logger.error(self.msg.invalid_json_payload(topic, payload))

        self.subscribe("devices/+/system", wrapper)


def _sync_worker(queue: Queue, stop_event: Event) -> None:
    """Worker thread that processes temperature data using synchronous database operations.

    Args:
        queue: Queue to read temperature data from.
        stop_event: Event to signal when to stop.

    """
    while not stop_event.is_set():
        try:
            # Non-blocking queue get with timeout
            item = queue.get(timeout=1)
            if item is None:  # Sentinel value to stop
                break

            device_id = item["device_id"]
            temperature = item["temperature"]
            timestamp = item["timestamp"]

            save_temperature_sync(device_id, temperature, timestamp)
        except QueueEmpty:
            # Queue timeout - continue processing
            continue


def run_subscriber(stop_event: Event | None = None) -> None:
    """Run the MQTT subscriber loop.

    Args:
        stop_event: Optional event used to stop the loop when set.

    """
    if stop_event is None:
        stop_event = Event()

    subscriber = MQTTSubscriber(MQTT_BACKEND_CONFIG)

    # Start sync worker thread for database operations
    worker_thread = Thread(target=_sync_worker, args=(subscriber.queue, stop_event), daemon=True)
    worker_thread.start()

    def handle_raspberry_telemetry(topic: str, data: dict[str, object]) -> None:
        """Handle incoming telemetry updates and queue for database save."""
        device_id = topic.split("/")[1]
        data_str = json.dumps(data)
        logger.info(f"[TELEMETRY UPDATE] | DEVICE: {device_id:<12} | DATA: {data_str}")

        # Extract temperature and timestamp from payload
        temperature_value = data.get("temperature")
        timestamp_value = data.get("timestamp")
        if temperature_value is not None and timestamp_value is not None:
            try:
                temp = float(temperature_value)
                # Handle both Unix timestamp (float) and ISO 8601 string formats
                if isinstance(timestamp_value, str):
                    dt = datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))
                    timestamp = dt.timestamp()
                else:
                    timestamp = float(timestamp_value)

                # Queue the temperature for processing by the sync worker
                subscriber.queue.put(
                    {
                        "device_id": device_id,
                        "temperature": temp,
                        "timestamp": timestamp,
                    }
                )
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid telemetry values: temperature={temperature_value}, timestamp={timestamp_value}, error: {e}")
        else:
            logger.warning("Telemetry payload missing temperature or timestamp")

    def handle_raspberry_status(topic: str, data: dict[str, object]) -> None:
        """Handle incoming system status updates and log them."""
        device_id = topic.split("/")[1]
        status = str(data.get("status", "unknown")).upper()
        logger.info(f"[SYSTEM STATUS] | DEVICE: {device_id:<12} | STATUS: {status}")

    subscriber.subscribe_raspberry_telemetry(handle_raspberry_telemetry)
    subscriber.subscribe_raspberry_system(handle_raspberry_status)

    subscriber.connect()

    try:
        import time

        while True:
            if stop_event.is_set():
                logger.info("Subscriber stop event received.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Subscriber manually stopped.")
    finally:
        subscriber.disconnect()
        stop_event.set()
        subscriber.queue.put(None)  # Sentinel to stop worker
        worker_thread.join(timeout=5)


def start_subscriber_thread() -> tuple[Thread, Event]:
    """Start the MQTT subscriber in a background thread.

    Returns:
        A tuple with the thread and its stop event.

    """
    stop_event = Event()
    thread = Thread(target=run_subscriber, args=(stop_event,), daemon=True)
    thread.start()
    return thread, stop_event


def save_temperature_sync(device_id: str, temperature: float, timestamp: float) -> None:
    """Save temperature data to the database using synchronous operations.

    Args:
        device_id: The unique identifier of the device.
        temperature: The temperature value in Celsius.
        timestamp: Unix timestamp from sensor (seconds).

    """
    with Session(sync_engine) as session:
        try:
            # Parse unix timestamp
            parsed_timestamp = datetime.fromtimestamp(timestamp, tz=UTC)

            # Create temperature record directly
            temp_record = Temperature(device_id=device_id, temperature=temperature, timestamp=parsed_timestamp)
            session.add(temp_record)
            session.commit()

            logger.info(f"Temperature saved: device={device_id}, temp={temperature}°C, timestamp={parsed_timestamp}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to save temperature: {e}")
        except ValueError as e:
            logger.error(f"Invalid temperature or timestamp data: device={device_id}, error={e}")


if __name__ == "__main__":
    run_subscriber()
