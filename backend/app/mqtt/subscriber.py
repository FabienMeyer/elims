"""ELIMS Backend - MQTT Subscriber Module."""

import asyncio
import json
import time
from collections.abc import Callable
from datetime import UTC
from threading import Event, Thread

from app.api.temperature.services import TemperatureService
from app.config import settings
from app.db import SessionLocal
from elims_common.logger.logger import logger
from elims_common.mqtt import MQTTConfig
from elims_common.mqtt import MQTTSubscriber as BaseMQTTSubscriber

CLIENT_TYPE = "subscriber"
CLIENT_ID = f"elims-backend-{CLIENT_TYPE}"

# Build MQTT config - always include certificate paths (even for plaintext, they just won't be used)
MQTT_BACKEND_CONFIG = MQTTConfig(
    broker_host=settings.mqtt_host,
    broker_port=settings.mqtt_port,
    username=settings.mqtt_username,
    password=settings.mqtt_password,
    client_id=CLIENT_ID,
    client_type=CLIENT_TYPE,
    lwt_topic=f"elims/{CLIENT_ID}/status",
    lwt_payload=json.dumps({"status": "offline"}),
    keepalive=60,
    reconnect_on_failure=True,
    certificate_authority_file=settings.mqtt_certificate_authority_file,
    certificate_file=settings.mqtt_certificate_file,
    key_file=settings.mqtt_key_file,
)


class MQTTSubscriber(BaseMQTTSubscriber):
    """Custom MQTT Subscriber for ELIMS."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize subscriber with environment defaults."""
        super().__init__(config)

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

        self.subscribe("devices/+/status", wrapper)


def run_subscriber(stop_event: Event | None = None) -> None:
    """Run the MQTT subscriber loop.

    Args:
        stop_event: Optional event used to stop the loop when set.

    """
    subscriber = MQTTSubscriber(MQTT_BACKEND_CONFIG)

    def handle_raspberry_telemetry(topic: str, data: dict[str, object]) -> None:
        """Handle incoming telemetry updates and save to database."""
        device_id = topic.split("/")[1]
        data_str = json.dumps(data)
        logger.info(f"[TELEMETRY UPDATE] | DEVICE: {device_id:<12} | DATA: {data_str}")

        # Extract temperature and timestamp from payload
        temperature_value = data.get("temperature")
        timestamp_value = data.get("timestamp")

        if temperature_value is not None and timestamp_value is not None:
            try:
                # Convert temperature to float
                temp_float = float(temperature_value)
                # Timestamp can be either a float (Unix timestamp) or a string (ISO format)
                asyncio.run(save_temperature(device_id, temp_float, timestamp_value))
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid telemetry values: temperature={temperature_value}, timestamp={timestamp_value}, error: {e}")
            except RuntimeError as e:
                logger.error(f"Failed to save temperature to database: {e}")
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
        while True:
            if stop_event is not None and stop_event.is_set():
                logger.info("Subscriber stop event received.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Subscriber manually stopped.")
    finally:
        subscriber.disconnect()


def start_subscriber_thread() -> tuple[Thread, Event]:
    """Start the MQTT subscriber in a background thread.

    Returns:
        A tuple with the thread and its stop event.

    """
    stop_event = Event()
    thread = Thread(target=run_subscriber, args=(stop_event,), daemon=True)
    thread.start()
    return thread, stop_event


async def save_temperature(device_id: str, temperature: float, timestamp: float | str) -> None:
    """Save temperature data to the database.

    Args:
        device_id: The unique identifier of the device.
        temperature: The temperature value in Celsius.
        timestamp: Unix timestamp from sensor (seconds) or ISO format string.

    """
    from datetime import datetime

    async with SessionLocal() as session:
        service = TemperatureService(session)
        from app.api.temperature.schemas import TemperatureCreate

        # Parse timestamp - handle both Unix timestamp and ISO format
        if isinstance(timestamp, str):
            # ISO format string (e.g., "2026-01-29T12:00:00Z")
            try:
                parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                logger.error(f"Could not parse ISO timestamp: {timestamp}, using current time")
                parsed_timestamp = datetime.now(UTC)
        else:
            # Unix timestamp (seconds)
            try:
                parsed_timestamp = datetime.fromtimestamp(float(timestamp), tz=UTC)
            except (ValueError, TypeError):
                logger.error(f"Could not parse Unix timestamp: {timestamp}, using current time")
                parsed_timestamp = datetime.now(UTC)

        temperature_data = TemperatureCreate(device_id=device_id, temperature=temperature, timestamp=parsed_timestamp)
        await service.create(temperature_data)

        logger.info(f"Temperature saved: device={device_id}, temp={temperature}°C, timestamp={parsed_timestamp}")


if __name__ == "__main__":
    run_subscriber()
