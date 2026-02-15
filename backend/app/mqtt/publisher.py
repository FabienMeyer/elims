"""ELIMS Backend - MQTT Publisher Module for sending configurations to devices."""

import json

from app.config import settings
from elims_common.logger.logger import logger
from elims_common.mqtt import MQTTConfig
from elims_common.mqtt import MQTTPublisher as BaseMQTTPublisher

CLIENT_TYPE = "publisher"
CLIENT_ID = f"elims-backend-{CLIENT_TYPE}"

# Build MQTT config for publisher with TLS/SSL
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


class MQTTPublisher(BaseMQTTPublisher):
    """Custom MQTT Publisher for ELIMS device configuration."""

    def __init__(self, config: MQTTConfig) -> None:
        """Initialize publisher with environment defaults.

        Args:
            config: The MQTT configuration.

        """
        super().__init__(config)

    def publish_device_config(self, device_id: str, config_data: dict) -> bool:
        """Publish configuration to a specific device.

        Args:
            device_id: The unique identifier of the device.
            config_data: Configuration dictionary to send.

        Returns:
            True if published successfully, False otherwise.

        """
        topic = f"devices/{device_id}/config"
        payload = json.dumps(config_data)
        try:
            result = self.publish(topic, payload)
            logger.info(f"[CONFIG PUBLISH] | DEVICE: {device_id:<12} | TOPIC: {topic} | STATUS: {'OK' if result else 'FAILED'}")
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to publish config to {device_id}: {e}")
            return False
        else:
            return result

    def publish_firmware_update(self, device_id: str, firmware_url: str, checksum: str = "") -> bool:
        """Publish firmware update notification to a device.

        Args:
            device_id: The unique identifier of the device.
            firmware_url: URL where firmware can be downloaded.
            checksum: Optional checksum for verification.

        Returns:
            True if published successfully, False otherwise.

        """
        topic = f"devices/{device_id}/firmware"
        payload = json.dumps({"url": firmware_url, "checksum": checksum, "enabled": True})
        try:
            result = self.publish(topic, payload)
            logger.info(f"[FIRMWARE UPDATE] | DEVICE: {device_id:<12} | URL: {firmware_url}")
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to publish firmware update to {device_id}: {e}")
            return False
        else:
            return result

    def publish_command(self, device_id: str, command: str, parameters: dict | None = None) -> bool:
        """Publish a command to a device.

        Args:
            device_id: The unique identifier of the device.
            command: The command to execute.
            parameters: Optional command parameters.

        Returns:
            True if published successfully, False otherwise.

        """
        topic = f"devices/{device_id}/command"
        payload = json.dumps({"command": command, "parameters": parameters or {}})
        try:
            result = self.publish(topic, payload)
            logger.info(f"[COMMAND PUBLISH] | DEVICE: {device_id:<12} | COMMAND: {command}")
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to publish command to {device_id}: {e}")
            return False
        else:
            return result


def get_publisher() -> MQTTPublisher:
    """Create and return an MQTT publisher instance.

    Returns:
        An MQTTPublisher instance.

    Raises:
        OSError: If connection fails after maximum retry attempts.

    """
    attempt = 0
    max_attempts = 3
    while attempt < max_attempts:
        try:
            publisher = MQTTPublisher(MQTT_BACKEND_CONFIG)
            publisher.connect()
            logger.info(f"[MQTT PUBLISHER] Connected: {MQTT_BACKEND_CONFIG.broker_host}:{MQTT_BACKEND_CONFIG.broker_port}")
        except (OSError, RuntimeError) as e:
            attempt += 1
            logger.error(f"Publisher connection attempt {attempt}/{max_attempts} failed: {e}")
            if attempt >= max_attempts:
                logger.error("Publisher: Failed to connect after maximum attempts")
                raise
        else:
            return publisher
    # Unreachable, but needed for type checker
    msg = "Failed to create publisher"
    raise OSError(msg)


if __name__ == "__main__":
    # Example usage
    publisher = get_publisher()
    try:
        # Send a test config
        publisher.publish_device_config("test-device-01", {"sample_rate": 5, "enabled": True})
    finally:
        publisher.disconnect()
