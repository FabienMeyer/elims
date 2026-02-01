"""ELIMS Raspberry Package - MQTT Module."""

import time
from collections.abc import Generator
from contextlib import contextmanager

from app.config import settings
from elims_common.logger.logger import logger
from elims_common.mqtt import MQTTConfig, MQTTPublisher

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
    client_id="raspberry-01",
)


# ---------------------------------------------------------------------
# PUBLISHER IMPLEMENTATION
# ---------------------------------------------------------------------


class RaspberryMQTTPublisher(MQTTPublisher):
    """Raspberry-specific MQTT Publisher."""

    def __init__(self, config: MQTTConfig | None = None) -> None:
        """Initialize publisher with environment defaults."""
        if config is None:
            config = RASPBERRY_MQTT_CONFIG
        super().__init__(config)

    def publish_sensor_data(self, sensor_id: str, data: dict) -> None:
        """Publish sensor data to standardized topic."""
        topic = f"devices/{self.config.client_id}/telemetry"
        # Include sensor_id in the payload instead
        payload = {"sensor_id": sensor_id, **data}
        self.publish(topic, payload)

    def publish_status(self, status: str) -> None:
        """Publish system status."""
        self.publish(
            f"devices/{self.config.client_id}/status",
            {"status": status},
            retain=True,
        )


# ---------------------------------------------------------------------
# CONTEXT MANAGER (OPTIONAL USE)
# ---------------------------------------------------------------------


@contextmanager
def mqtt_publisher(config: MQTTConfig) -> Generator[MQTTPublisher]:
    """Context manager for MQTT publisher."""
    publisher = RaspberryMQTTPublisher(config)
    try:
        publisher.connect()
        yield publisher
    finally:
        if publisher.is_connected:
            publisher.publish("raspberry/status", {"status": "offline"}, retain=True)
            publisher.disconnect()


# ---------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------


def main() -> None:
    """MQTT publisher."""
    logger.info(f"Connecting to MQTT broker at " f"{RASPBERRY_MQTT_CONFIG.broker_host}:" f"{RASPBERRY_MQTT_CONFIG.broker_port}")

    publisher = RaspberryMQTTPublisher(RASPBERRY_MQTT_CONFIG)

    try:
        # --- CONNECT ONCE ---
        publisher.connect()
        logger.info("Connected to MQTT broker")

        # Publish online status once
        publisher.publish_status("online")
        logger.info("Published status: online")

        # --- PUBLISH LOOP ---
        while True:
            sensor_data = {
                "temperature": 22.5,
                "humidity": 45.0,
                "timestamp": "2026-01-29T12:00:00Z",
            }

            publisher.publish_sensor_data("sensor_01", sensor_data)
            logger.info(f"Published sensor data: {sensor_data}")

            time.sleep(10)

    except KeyboardInterrupt:
        logger.warning("Shutdown requested by user")

    finally:
        # --- CLEAN SHUTDOWN ---
        if publisher.is_connected:
            publisher.publish_status("offline")
            publisher.disconnect()
        logger.info("Disconnected from MQTT broker")


# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
