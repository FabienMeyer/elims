# ELIMS Raspberry Package

## Overview

`elims-raspberry` is a specialized Python package designed for running ELIMS components on Raspberry Pi devices. It provides lightweight data collection, instrument communication, and edge computing capabilities for laboratory equipment interfacing.

## Package Information

- **Name**: elims-raspberry
- **Version**: 0.0.1
- **Python**: 3.13+
- **License**: MIT
- **Platform**: Raspberry Pi (compatible with other Linux systems)

## Installation

### Prerequisites

- Raspberry Pi (3B+ or newer recommended)
- Raspberry Pi OS (64-bit recommended)
- Python 3.13+
- Network connectivity

### From Source

```bash
# Navigate to package directory
cd packages/elims-raspberry

# Install in development mode
uv pip install -e .

# Or with development dependencies
uv pip install -e ".[dev]"
```

### System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13 (if not available)
sudo apt install python3.13 python3.13-venv python3.13-dev

# Install system libraries
sudo apt install -y \
    libgpiod2 \
    i2c-tools \
    python3-smbus \
    git
```

## Package Structure

```
elims-raspberry/
├── elims_raspberry/
│   ├── __init__.py
│   └── elims_raspberry.py   # Main module
├── tests/
│   ├── __init__.py
│   └── test_elims_raspberry.py
├── pyproject.toml           # Package configuration
└── README.md
```

## Core Features

### 1. GPIO Control

Interface with laboratory equipment via GPIO pins:

```python
from elims_raspberry import GPIOController
from elims_raspberry.enums import PinMode, PinState

class EquipmentController:
    """Control equipment via GPIO"""

    def __init__(self):
        self.gpio = GPIOController()

    def setup_relay(self, pin: int):
        """Setup relay control pin"""
        self.gpio.setup_pin(pin, PinMode.OUTPUT)

    def turn_on(self, pin: int):
        """Turn on equipment"""
        self.gpio.write_pin(pin, PinState.HIGH)

    def turn_off(self, pin: int):
        """Turn off equipment"""
        self.gpio.write_pin(pin, PinState.LOW)

    def read_sensor(self, pin: int) -> bool:
        """Read digital sensor"""
        self.gpio.setup_pin(pin, PinMode.INPUT)
        state = self.gpio.read_pin(pin)
        return state == PinState.HIGH

    def cleanup(self):
        """Cleanup GPIO"""
        self.gpio.cleanup()

# Usage
controller = EquipmentController()
controller.setup_relay(17)
controller.turn_on(17)
# ... do work ...
controller.turn_off(17)
controller.cleanup()
```

### 2. Serial Communication

Communicate with instruments via serial port:

```python
from elims_raspberry import SerialDevice
import time

class InstrumentReader:
    """Read data from serial instruments"""

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        self.device = SerialDevice(
            port=port,
            baudrate=baudrate,
            timeout=1.0,
        )

    def connect(self):
        """Connect to instrument"""
        self.device.open()

    def read_measurement(self) -> str:
        """Read measurement from instrument"""
        # Send command
        self.device.write(b"MEAS?\n")

        # Wait for response
        time.sleep(0.1)

        # Read response
        response = self.device.read_line()
        return response.decode('ascii').strip()

    def configure(self, settings: dict):
        """Configure instrument"""
        for key, value in settings.items():
            command = f"{key}:{value}\n".encode('ascii')
            self.device.write(command)
            time.sleep(0.05)

    def disconnect(self):
        """Disconnect from instrument"""
        self.device.close()

# Usage
reader = InstrumentReader(port="/dev/ttyUSB0")
reader.connect()
measurement = reader.read_measurement()
print(f"Measurement: {measurement}")
reader.disconnect()
```

### 3. I2C Communication

Interface with I2C sensors and devices:

```python
from elims_raspberry import I2CDevice

class TemperatureSensor:
    """Read temperature from I2C sensor"""

    # Common I2C addresses
    BMP280_ADDR = 0x76
    BME280_ADDR = 0x77

    def __init__(self, address: int = BME280_ADDR, bus: int = 1):
        self.device = I2CDevice(address=address, bus=bus)
        self.initialize()

    def initialize(self):
        """Initialize sensor"""
        # Write configuration to registers
        self.device.write_byte(0xF4, 0x27)  # Control register
        self.device.write_byte(0xF5, 0xA0)  # Config register

    def read_temperature(self) -> float:
        """Read temperature in Celsius"""
        # Read raw data from registers
        msb = self.device.read_byte(0xFA)
        lsb = self.device.read_byte(0xFB)
        xlsb = self.device.read_byte(0xFC)

        # Combine bytes
        raw_temp = (msb << 12) | (lsb << 4) | (xlsb >> 4)

        # Convert to temperature (simplified)
        temperature = (raw_temp / 16384.0) - 273.15

        return round(temperature, 2)

    def read_humidity(self) -> float:
        """Read humidity percentage"""
        msb = self.device.read_byte(0xFD)
        lsb = self.device.read_byte(0xFE)

        raw_humidity = (msb << 8) | lsb
        humidity = (raw_humidity / 65536.0) * 100

        return round(humidity, 2)

# Usage
sensor = TemperatureSensor()
temp = sensor.read_temperature()
humidity = sensor.read_humidity()
print(f"Temperature: {temp}°C, Humidity: {humidity}%")
```

### 4. MQTT Client

Publish sensor data to MQTT broker:

```python
from elims_raspberry import MQTTPublisher
import time

class DataPublisher:
    """Publish sensor data via MQTT"""

    def __init__(self, broker: str, port: int = 1883):
        self.publisher = MQTTPublisher(
            broker=broker,
            port=port,
            client_id="raspberry-pi-01",
        )
        self.topic_prefix = "lab/instruments"

    def connect(self, username: str = None, password: str = None):
        """Connect to MQTT broker"""
        if username and password:
            self.publisher.set_credentials(username, password)

        self.publisher.connect()

    def publish_measurement(self, instrument_id: str, measurement: dict):
        """Publish measurement data"""
        topic = f"{self.topic_prefix}/{instrument_id}/measurement"
        self.publisher.publish(topic, measurement)

    def publish_status(self, instrument_id: str, status: str):
        """Publish instrument status"""
        topic = f"{self.topic_prefix}/{instrument_id}/status"
        self.publisher.publish(topic, {"status": status})

    def disconnect(self):
        """Disconnect from broker"""
        self.publisher.disconnect()

# Usage
publisher = DataPublisher(broker="mqtt.example.com")
publisher.connect(username="user", password="pass")

# Publish measurement
publisher.publish_measurement(
    "INSTRUMENT-001",
    {
        "temperature": 25.5,
        "humidity": 45.2,
        "timestamp": "2026-01-23T10:30:00Z"
    }
)

publisher.disconnect()
```

### 5. Data Logger

Log sensor data locally:

```python
from elims_raspberry import DataLogger
from datetime import datetime

class LocalLogger:
    """Log measurements to local storage"""

    def __init__(self, log_dir: str = "/var/log/elims"):
        self.logger = DataLogger(
            log_dir=log_dir,
            rotation_size="10MB",
            retention_days=30,
        )

    def log_measurement(self, instrument_id: str, data: dict):
        """Log measurement data"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "instrument_id": instrument_id,
            "data": data,
        }
        self.logger.write(entry)

    def log_event(self, event_type: str, message: str):
        """Log system event"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "message": message,
        }
        self.logger.write(entry, log_name="events")

    def get_logs(self, start_date: str = None, end_date: str = None):
        """Retrieve logs within date range"""
        return self.logger.query(start_date, end_date)

# Usage
logger = LocalLogger()
logger.log_measurement("INST-001", {"temp": 25.5})
logger.log_event("startup", "System initialized")
```

## Configuration

### Device Configuration

```python
from pydantic import BaseModel, Field
from typing import Optional

class RaspberryPiConfig(BaseModel):
    """Raspberry Pi configuration"""

    device_id: str = Field(..., description="Unique device identifier")
    location: str = Field(..., description="Physical location")

    # MQTT Configuration
    mqtt_broker: str
    mqtt_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_topic_prefix: str = "lab/instruments"

    # Sampling Configuration
    sampling_interval: int = Field(default=60, ge=1, description="Seconds between samples")
    batch_size: int = Field(default=10, ge=1, description="Number of samples per batch")

    # Storage Configuration
    log_directory: str = "/var/log/elims"
    max_log_size: str = "10MB"
    log_retention_days: int = 30

    # GPIO Configuration
    gpio_pins: dict = Field(default_factory=dict)

    class Config:
        env_prefix = "ELIMS_"

# Load configuration
config = RaspberryPiConfig(
    device_id="RPI-LAB-001",
    location="Laboratory A",
    mqtt_broker="mqtt.example.com",
)
```

## Complete Example: Temperature Monitor

```python
#!/usr/bin/env python3
"""
Temperature monitoring system for Raspberry Pi
Reads temperature from sensor and publishes to MQTT
"""

from elims_raspberry import (
    I2CDevice,
    MQTTPublisher,
    DataLogger,
    GPIOController,
)
from elims_raspberry.config import RaspberryPiConfig
import time
import signal
import sys

class TemperatureMonitor:
    """Monitor and publish temperature data"""

    def __init__(self, config: RaspberryPiConfig):
        self.config = config
        self.running = False

        # Initialize components
        self.sensor = I2CDevice(address=0x76)
        self.mqtt = MQTTPublisher(
            broker=config.mqtt_broker,
            port=config.mqtt_port,
            client_id=config.device_id,
        )
        self.logger = DataLogger(log_dir=config.log_directory)
        self.gpio = GPIOController()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def start(self):
        """Start monitoring"""
        print(f"Starting temperature monitor: {self.config.device_id}")

        # Connect to MQTT
        if self.config.mqtt_username:
            self.mqtt.set_credentials(
                self.config.mqtt_username,
                self.config.mqtt_password,
            )
        self.mqtt.connect()

        # Initialize sensor
        self.sensor.write_byte(0xF4, 0x27)

        # Start monitoring loop
        self.running = True
        self.monitor_loop()

    def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Read temperature
                temp = self.read_temperature()

                # Prepare data
                data = {
                    "device_id": self.config.device_id,
                    "location": self.config.location,
                    "temperature": temp,
                    "unit": "celsius",
                    "timestamp": time.time(),
                }

                # Publish to MQTT
                topic = f"{self.config.mqtt_topic_prefix}/{self.config.device_id}/temperature"
                self.mqtt.publish(topic, data)

                # Log locally
                self.logger.write(data)

                print(f"Temperature: {temp}°C")

                # Wait for next sample
                time.sleep(self.config.sampling_interval)

            except Exception as e:
                print(f"Error: {e}")
                self.logger.write({"error": str(e)}, log_name="errors")
                time.sleep(5)

    def read_temperature(self) -> float:
        """Read temperature from sensor"""
        msb = self.sensor.read_byte(0xFA)
        lsb = self.sensor.read_byte(0xFB)
        xlsb = self.sensor.read_byte(0xFC)

        raw_temp = (msb << 12) | (lsb << 4) | (xlsb >> 4)
        temperature = (raw_temp / 16384.0) - 273.15

        return round(temperature, 2)

    def shutdown(self, signum, frame):
        """Graceful shutdown"""
        print("\nShutting down...")
        self.running = False
        self.mqtt.disconnect()
        self.gpio.cleanup()
        sys.exit(0)

if __name__ == "__main__":
    # Load configuration
    config = RaspberryPiConfig(
        device_id="RPI-LAB-001",
        location="Laboratory A",
        mqtt_broker="mqtt.example.com",
        mqtt_username="lab_user",
        mqtt_password="secure_password",
        sampling_interval=30,
    )

    # Start monitor
    monitor = TemperatureMonitor(config)
    monitor.start()
```

## Systemd Service

Create a systemd service for automatic startup:

```ini
# /etc/systemd/system/elims-monitor.service
[Unit]
Description=ELIMS Temperature Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/elims
ExecStart=/home/pi/elims/.venv/bin/python /home/pi/elims/monitor.py
Restart=always
RestartSec=10
Environment="ELIMS_DEVICE_ID=RPI-LAB-001"
Environment="ELIMS_MQTT_BROKER=mqtt.example.com"

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
# Enable service
sudo systemctl enable elims-monitor.service

# Start service
sudo systemctl start elims-monitor.service

# Check status
sudo systemctl status elims-monitor.service

# View logs
sudo journalctl -u elims-monitor.service -f
```

## Hardware Setup

### GPIO Pinout

Common GPIO pin usage:

```
Pin 1  (3.3V)     Pin 2  (5V)
Pin 3  (GPIO 2)   Pin 4  (5V)
Pin 5  (GPIO 3)   Pin 6  (GND)
Pin 7  (GPIO 4)   Pin 8  (GPIO 14)
Pin 9  (GND)      Pin 10 (GPIO 15)
Pin 11 (GPIO 17)  Pin 12 (GPIO 18)
...
```

### I2C Devices

Enable I2C:

```bash
# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable

# Reboot
sudo reboot

# Test I2C
i2cdetect -y 1
```

### Serial Devices

Enable serial:

```bash
# Enable serial
sudo raspi-config
# Navigate to: Interface Options > Serial Port
# Disable login shell, Enable serial hardware

# Reboot
sudo reboot
```

## Development

### Setup Development Environment

```bash
# Install package in development mode
cd packages/elims-raspberry
uv pip install -e ".[dev]"

# Install system dependencies
sudo apt install -y \
    libgpiod2 \
    i2c-tools \
    python3-smbus
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=elims_raspberry --cov-report=html

# Run hardware tests (requires actual hardware)
pytest -m hardware
```

### Mock Hardware for Testing

```python
from unittest.mock import Mock, patch

class TestTemperatureSensor:
    """Test sensor with mocked hardware"""

    @patch('elims_raspberry.I2CDevice')
    def test_read_temperature(self, mock_i2c):
        """Test temperature reading"""
        # Setup mock
        mock_device = Mock()
        mock_device.read_byte.side_effect = [0x80, 0x00, 0x00]
        mock_i2c.return_value = mock_device

        # Test
        sensor = TemperatureSensor()
        temp = sensor.read_temperature()

        # Assert
        assert isinstance(temp, float)
        assert -40 <= temp <= 85  # Valid temperature range
```

## Best Practices

1. **Error Handling**: Always handle hardware errors gracefully
1. **Resource Cleanup**: Use context managers or cleanup methods
1. **Power Management**: Consider power consumption on battery
1. **Network Resilience**: Handle network disconnections
1. **Data Buffering**: Buffer data locally before sending
1. **Security**: Secure MQTT connections with TLS
1. **Logging**: Log all errors and important events
1. **Testing**: Use mocks for hardware-dependent tests

## Troubleshooting

### Common Issues

1. **Permission Denied on GPIO/I2C**

   ```bash
   sudo usermod -a -G gpio,i2c,spi $USER
   sudo reboot
   ```

1. **I2C Device Not Found**

   ```bash
   # Check I2C is enabled
   ls /dev/i2c-*

   # Scan for devices
   i2cdetect -y 1
   ```

1. **Serial Port Access Denied**

   ```bash
   sudo usermod -a -G dialout $USER
   sudo reboot
   ```

1. **MQTT Connection Failed**

   - Check network connectivity
   - Verify broker address and port
   - Check firewall rules
   - Verify credentials

## Dependencies

### Core Dependencies

- `pydantic>=2.0.0`: Configuration management
- `pydantic-settings>=2.0.0`: Settings from environment

### Optional Dependencies

- `RPi.GPIO`: GPIO control (hardware-specific)
- `smbus2`: I2C communication
- `pyserial`: Serial communication
- `paho-mqtt`: MQTT client

### Development Dependencies

- `pytest>=7.4.0`: Testing
- `pytest-cov>=4.1.0`: Coverage
- `ruff>=0.1.0`: Linting
- `mypy>=1.5.0`: Type checking

## License

MIT License - see LICENSE file for details

## Related Documentation

- [Backend Documentation](../../backend/index.md)
- [ELIMS Common Package](../elims-common/index.md)
- [Workflows Documentation](../../workflows/index.md)
