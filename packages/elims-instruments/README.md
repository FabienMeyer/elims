# elims-instruments

Framework-independent instrument-domain models for ELIMS.

```python
from elims_instruments import Instrument

instrument = Instrument(identifier="scope-1", name="Oscilloscope")
```

See the repository documentation for architectural guidance and the generated API reference.

## Documentation

```bash
uv sync --extra docs
uv run mkdocs serve
```
