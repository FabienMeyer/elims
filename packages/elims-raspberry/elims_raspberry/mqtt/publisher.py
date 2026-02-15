"""ELIMS Raspberry Package - MQTT Module."""

import json
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime

import adafruit_bmp280
import adafruit_dht
import board
from app.config import settings
from elims_common.logger.logger import logger
from elims_common.mqtt import MQTTConfig, MQTTPublisher

# ---------------------------------------------------------------------
# MQTT CONFIG
# ---------------------------------------------------------------------

CLIENT_TYPE = "publisher"
CLIENT_ID = f"elims-raspberry-01-{CLIENT_TYPE}"
RASPBERRY_MQTT_CONFIG = MQTTConfig(
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


# ---------------------------------------------------------------------
# PUBLISHER IMPLEMENTATION
# ---------------------------------------------------------------------


class RaspberryMQTTPublisher(MQTTPublisher):
    """Raspberry-specific MQTT Publisher."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize publisher with environment defaults."""
        super().__init__(config)

    def publish_raspberry_telemetry(self, sensor_id: str, data: dict[str, object]) -> None:
        """Publish raspberry telemetry data to a topic."""
        topic = f"devices/{self.config.client_id}/telemetry"
        payload = {"sensor_id": sensor_id, **data}
        self.publish(topic, payload)
        logger.info(self.msg.publishing(topic=topic, payload=payload))

    def publish_raspberry_status(self, status: str) -> None:
        """Publish raspberry status (online/offline) with retain flag."""
        topic = f"devices/{self.config.client_id}/status"
        payload = {"status": status}
        self.publish(topic, payload)
        logger.info(self.msg.publishing(topic=topic, payload=payload))


@contextmanager
def mqtt_publisher(config: MQTTConfig) -> Generator[MQTTPublisher]:
    """Context manager for MQTT publisher."""
    publisher = RaspberryMQTTPublisher(config)
    try:
        publisher.connect()
        yield publisher
    finally:
        if publisher.is_connected:
            publisher.publish_raspberry_status("offline")
            publisher.disconnect()


def main() -> None:
    """MQTT publisher."""
    publisher = RaspberryMQTTPublisher(RASPBERRY_MQTT_CONFIG)

    try:
        publisher.connect()
        publisher.publish_raspberry_status("online")

        i2c = board.I2C()  # uses board.SCL and board.SDA
        bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        dht11 = adafruit_dht.DHT11(board.D22)

        while True:
            now = datetime.now(UTC)
            timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

            sensor_data = {
                "timestamp": timestamp,
            }

            # Read BMP280 temperature (pressure sensor)
            try:
                sensor_data["temperature"] = bmp280.temperature
            except (RuntimeError, OSError) as e:
                logger.error(f"Failed to read BMP280 temperature: {e}")

            # Read DHT11 humidity sensor
            try:
                sensor_data["humidity"] = dht11.humidity
            except (RuntimeError, OSError) as e:
                logger.error(f"Failed to read DHT11 humidity: {e}")

            # Only publish if we have at least one sensor reading
            if len(sensor_data) > 1:  # More than just timestamp
                publisher.publish_raspberry_telemetry("sensor_01", sensor_data)
            else:
                logger.warning("No sensor data available, skipping publish cycle")

            time.sleep(10)

    except KeyboardInterrupt:
        logger.warning("Shutdown requested by user")

    finally:
        if publisher.is_connected:
            publisher.publish_raspberry_status("offline")
            publisher.disconnect()


if __name__ == "__main__":
    main()
