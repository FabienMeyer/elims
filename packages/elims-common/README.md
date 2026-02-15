# ELIMS - Electronic Laboratory Instrument Management System - Common Package

## Overview

The `elims-common` package provides shared functionality for the ELIMS system, including MQTT publisher and subscriber components for cross-system communication.

## Installation

```bash
pip install -e packages/elims-common
```

## Features

- **MQTT Publisher**: Publish messages to MQTT topics
- **MQTT Subscriber**: Subscribe to MQTT topics and handle incoming messages
- **Configuration**: Pydantic-based configuration with validation
- **Type Safety**: Full type hints and mypy compatibility

## MQTT Usage

### Publisher Example

```python
from elims_common import MQTTConfig, MQTTPublisher

# Configure MQTT connection
config = MQTTConfig(
    broker_host="localhost",
    broker_port=8883,
    username="your_username",  # Optional
    password="your_password",  # Optional
    client_id="publisher_client",
    qos=1,
)

# Create and connect publisher
publisher = MQTTPublisher(config)
publisher.connect()

# Publish string message
publisher.publish("sensors/temperature", "23.5")

# Publish dictionary (automatically converted to JSON)
publisher.publish("sensors/data", {
    "temperature": 23.5,
    "humidity": 65.0,
})

# Disconnect when done
publisher.disconnect()
```

### Subscriber Example

```python
from elims_common import MQTTConfig, MQTTSubscriber

# Configure MQTT connection
config = MQTTConfig(
    broker_host="localhost",
    broker_port=8883,
    qos=1,
)

# Create subscriber
subscriber = MQTTSubscriber(config)

# Define callback function
def on_temperature(topic: str, payload: str):
    print(f"Received on {topic}: {payload}")

# Subscribe to topics
subscriber.subscribe("sensors/temperature", on_temperature)
subscriber.subscribe("sensors/#", on_temperature)  # Wildcard subscription

# Connect and start receiving messages
subscriber.connect()

# Keep running (or use in async context)
import time
while True:
    time.sleep(1)
```

## Configuration Options

- `broker_host`: MQTT broker hostname (default: "localhost")
- `broker_port`: MQTT broker port (default: 8883)
- `username`: Authentication username (optional)
- `password`: Authentication password (optional)
- `client_id`: Unique client identifier (optional)
- `keepalive`: Keepalive interval in seconds (default: 60)
- `clean_session`: Clean session flag (default: True)
- `qos`: Quality of Service level 0, 1, or 2 (default: 1)

## Development

### Running Tests

```bash
cd packages/elims-common
pytest
```

### Type Checking

```bash
mypy elims_common
```
