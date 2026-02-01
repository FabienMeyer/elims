"""ELIMS Backend - MQTT Subscriber Module."""

import json
import time
from collections.abc import Callable

from app.config import settings
from elims_common.logger.logger import logger
from elims_common.mqtt import MQTTConfig
from elims_common.mqtt import MQTTSubscriber as BaseMQTTSubscriber

# ---------------------------------------------------------------------
# MQTT CONFIG
# ---------------------------------------------------------------------

RASPBERRY_MQTT_CONFIG = MQTTConfig(
    broker_host=settings.mqtt_host,
    broker_port=settings.mqtt_port,
    username=settings.mqtt_username,
    password=settings.mqtt_password,
    keepalive=60,
    reconnect_on_failure=True,
    client_id="fastapi",
    use_tls=bool(settings.mqtt_ca_file),
    certificate_authority_file=settings.mqtt_ca_file,
)


class MQTTSubscriber(BaseMQTTSubscriber):
    """Custom MQTT Subscriber for ELIMS."""

    def __init__(self, config: MQTTConfig | None = None) -> None:
        """Initialize subscriber with environment defaults."""
        if config is None:
            config = RASPBERRY_MQTT_CONFIG
        super().__init__(config)

    def subscribe_all_sensors(self, callback: Callable[[str, dict[str, object]], None]) -> None:
        """Subscribe to all sensor telemetry data from devices."""

        def wrapper(topic: str, payload: str) -> None:
            try:
                data = json.loads(payload)
                callback(topic, data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from {topic}: {payload}")

        self.subscribe("devices/+/telemetry", wrapper)

    def subscribe_system_status(self, callback: Callable[[str, dict[str, object]], None]) -> None:
        """Subscribe to device status updates (online/offline)."""

        def wrapper(topic: str, payload: str) -> None:
            try:
                data = json.loads(payload)
                callback(topic, data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from {topic}: {payload}")

        self.subscribe("devices/+/status", wrapper)


def main() -> None:
    """MQTT subscriber for ELIMS backend."""
    subscriber = MQTTSubscriber(RASPBERRY_MQTT_CONFIG)

    def handle_sensor_data(topic: str, data: dict[str, object]) -> None:
        # Extract the device ID from the topic (e.g., 'raspberry-01')
        device_id = topic.split("/")[1]
        sensor_id = data.get("sensor_id", "unknown")

        # Create a clean string representation of the data
        data_str = json.dumps(data)

        # Log with a specific format to make it stand out
        logger.info(f"⚡ [SENSOR UPDATE] | DEVICE: {device_id:<12} | SENSOR: {sensor_id:<12} | DATA: {data_str}")

    def handle_status(topic: str, status: dict[str, object]) -> None:
        device_id = topic.split("/")[1]
        logger.info(f"🌐 [SYSTEM STATUS] | DEVICE: {device_id} | {status.get('status', 'unknown').upper()}")

    # Wire up the callbacks
    subscriber.subscribe_all_sensors(handle_sensor_data)
    subscriber.subscribe_system_status(handle_status)

    subscriber.connect()
    try:
        logger.info("ELIMS Subscriber Active. Listening for sensor data...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Subscriber manually stopped.")
        subscriber.disconnect()


if __name__ == "__main__":
    main()
