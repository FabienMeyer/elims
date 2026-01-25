"""ELIMS Raspberry Package - MQTT Module."""

from collections.abc import Generator
from contextlib import contextmanager

from elims_common.mqtt import MQTTConfig, MQTTPublisher

RASPBERRY_MQTT_CONFIG = MQTTConfig(
    broker_address="raspberry.local",
    broker_port=1883,
    username="raspberry_user",
    password="raspberry_pass",  # noqa: S106
    keepalive=60,
)


class RaspberryMQTTPublisher(MQTTPublisher):
    """Raspberry-specific MQTT Publisher."""

    def __init__(self, config: MQTTConfig | None = None) -> None:
        """Initialize with default config if not provided."""
        if config is None:
            config = MQTTConfig(
                broker_host="raspberry.local",
                broker_port=1883,
                username="raspberry_user",
                password="raspberry_pass",  # noqa: S106
                keepalive=60,
                reconnect_on_failure=True,
            )
        super().__init__(config)

    def publish_sensor_data(self, sensor_id: str, data: dict) -> None:
        """Publish sensor data to standardized topic."""
        topic = f"raspberry/sensors/{sensor_id}"
        self.publish(topic, data)

    def publish_status(self, status: str) -> None:
        """Publish system status."""
        self.publish("raspberry/status", {"status": status}, retain=True)


@contextmanager
def mqtt_publisher(config: MQTTConfig) -> Generator[MQTTPublisher]:
    """Context manager for MQTT publisher."""
    publisher = MQTTPublisher(config)
    try:
        publisher.connect()
        yield publisher
    finally:
        publisher.disconnect()
