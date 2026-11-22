# elims-utils

`elims-utils` provides small, framework-independent helpers shared by ELIMS packages.

## Installation

```bash
pip install elims-utils
```

## Usage

```python
from elims_utils import utc_now

created_at = utc_now()
```

The returned `datetime` is timezone-aware and uses UTC explicitly.
