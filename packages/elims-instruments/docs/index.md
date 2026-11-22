# elims-instruments

`elims-instruments` provides framework-independent instrument-domain models.

## Installation

```bash
pip install elims-instruments
```

## Usage

```python
from elims_instruments import Instrument

instrument = Instrument(identifier="scope-1", name="Oscilloscope")
```

`Instrument` is an immutable, slotted domain entity.
