# elims-com

`elims-com` defines communication contracts without selecting a broker, protocol, or network client.

## Installation

```bash
pip install elims-com
```

## Usage

```python
from elims_com import JsonMessageCodec, Message

message = Message(subject="sample.created", payload={"sample_id": 42})
encoded = JsonMessageCodec.encode(message)
decoded = JsonMessageCodec.decode(encoded)
```

Messages receive a UUID and a timezone-aware UTC timestamp by default.
