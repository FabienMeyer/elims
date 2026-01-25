"""ELIMS Raspberry Package - MQTT Module."""

import json
from collections.abc import Callable, Generator
from contextlib import contextmanager

import adafruit_bmp280
import adafruit_dht
import board
import busio
from elims_common.logger.logger import logger
from elims_common.mqtt import MQTTConfig, MQTTSubscriber


def raspberry_sensor() -> tuple[float, float, float, float]:
    """Read and log sensor data from Raspberry Pi sensors."""
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)
        dht = adafruit_dht.DHT11(board.D22)
        temperature = bmp.temperature
        pressure = bmp.pressure
        altitude = bmp.altitude
        humidity = dht.humidity
        logger.info(f"Temperature={temperature:.3f}[°C], Pressure={pressure:.3f}[hPa], Altitude={altitude:.3f}[m], Humidity={humidity}[%]")

    except RuntimeError as e:
        logger.warning(f"Failed to read DHT sensor: {e}")
    except OSError as e:
        logger.error(f"Error reading sensors: {e}")
    finally:
        dht.exit()
    return temperature, pressure, altitude, humidity


class MQTTSubscriber(MQTTSubscriber):
    """Backend-specific MQTT Subscriber for handling sensor data and alerts."""

    def __init__(self, config: MQTTConfig | None = None) -> None:
        """Initialize with default config if not provided."""
        if config is None:
            config = MQTTConfig(
                broker_host="localhost",
                broker_port=1883,
                username="backend_user",
                password="backend_pass",  # noqa: S106
                keepalive=60,
                reconnect_on_failure=True,
                log_payloads=True,
                max_payload_log_length=200,
            )
        super().__init__(config)

    def subscribe_all_sensors(self, callback: Callable[[str, dict], None]) -> None:
        """Subscribe to all sensor data with wildcard."""

        def wrapper(topic: str, payload: str) -> None:
            try:
                data = json.loads(payload)
                callback(topic, data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from {topic}: {payload}")

        self.subscribe("sensors/+/data", wrapper)

    def subscribe_specific_sensor(self, sensor_id: str, callback: Callable[[str, dict], None]) -> None:
        """Subscribe to specific sensor data."""
        topic = f"sensors/{sensor_id}/data"

        def wrapper(topic: str, payload: str) -> None:
            try:
                data = json.loads(payload)
                callback(topic, data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from {topic}: {payload}")

        self.subscribe(topic, wrapper)

    def subscribe_alerts(self, callback: Callable[[str, str], None]) -> None:
        """Subscribe to all alert topics."""
        self.subscribe("alerts/#", callback)

    def subscribe_system_status(self, callback: Callable[[str, dict], None]) -> None:
        """Subscribe to system status updates."""

        def wrapper(topic: str, payload: str) -> None:
            try:
                data = json.loads(payload)
                callback(topic, data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from {topic}: {payload}")

        self.subscribe("system/+/status", wrapper)


@contextmanager
def mqtt_subscriber(config: MQTTConfig) -> Generator[MQTTSubscriber]:
    """Context manager for MQTT subscriber."""
    subscriber = MQTTSubscriber(config)
    try:
        subscriber.connect()
        yield subscriber
    finally:
        subscriber.disconnect()


# Example usage
def main() -> None:
    """Run example MQTT subscriber."""
    subscriber = MQTTSubscriber()

    # Define handlers
    def handle_sensor_data(topic: str, data: dict) -> None:
        logger.info(f"Sensor data from {topic}: {data}")
        # Process data (save to database, trigger actions, etc.)

    def handle_alert(topic: str, message: str) -> None:
        logger.warning(f"Alert from {topic}: {message}")
        # Handle alert (notify admin, log to DB, etc.)

    def handle_status(topic: str, status: dict) -> None:
        logger.info(f"Status update from {topic}: {status}")
        # Update system status

    # Subscribe to topics
    subscriber.subscribe_all_sensors(handle_sensor_data)
    subscriber.subscribe_alerts(handle_alert)
    subscriber.subscribe_system_status(handle_status)

    # Connect and run
    subscriber.connect()

    try:
        logger.info("Subscriber running. Press Ctrl+C to stop.")
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down subscriber...")
        subscriber.disconnect()


if __name__ == "__main__":
    main()
