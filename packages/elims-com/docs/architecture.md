# Architecture

The package contains transport-neutral communication contracts.

- `models.py` defines validated message models.
- `codec.py` provides deterministic JSON serialization.
- `protocols.py` defines ports implemented by transport adapters.

Concrete MQTT, AMQP, HTTP, or other transport clients belong in adapter packages.
