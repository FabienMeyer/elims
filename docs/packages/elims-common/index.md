# ELIMS Common Package

## Overview

`elims-common` is a shared Python package containing common utilities, models, and functions used across the ELIMS ecosystem. It provides reusable components for data validation, configuration management, and shared business logic.

## Package Information

- **Name**: elims-common
- **Version**: 0.0.1
- **Python**: 3.13+
- **License**: MIT

## Installation

### From Source

```bash
# Navigate to package directory
cd packages/elims-common

# Install in development mode
uv pip install -e .

# Or with development dependencies
uv pip install -e ".[dev]"
```

### As Dependency

Add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "elims-common @ file:///path/to/packages/elims-common",
]
```

## Package Structure

```
elims-common/
├── elims_common/
│   ├── __init__.py
│   └── elims_elims.py     # Main module
├── tests/
│   ├── __init__.py
│   └── test_elims.py      # Test suite
├── pyproject.toml         # Package configuration
└── README.md
```

## Core Components

### 1. Pydantic Models

Base models for data validation and serialization:

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class BaseInstrument(BaseModel):
    """Base model for laboratory instruments"""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
    )

    name: str = Field(..., min_length=1, max_length=255)
    model: str = Field(..., min_length=1, max_length=255)
    serial_number: str = Field(..., min_length=1, max_length=255)
    manufacturer: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|inactive|maintenance)$")

    def is_active(self) -> bool:
        """Check if instrument is active"""
        return self.status == "active"

class BaseLocation(BaseModel):
    """Base model for laboratory locations"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255)
    building: str
    floor: Optional[int] = None
    room: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0)
```

### 2. Configuration Utilities

Shared configuration management:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class DatabaseConfig(BaseSettings):
    """Database configuration"""

    host: str
    port: int = 3306
    user: str
    password: str
    database: str

    model_config = {
        "env_prefix": "MARIADB_",
    }

    @property
    def url(self) -> str:
        """Get database URL"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class CacheConfig(BaseSettings):
    """Cache configuration"""

    host: str
    port: int = 6379
    password: Optional[str] = None
    db: int = 0

    model_config = {
        "env_prefix": "REDIS_",
    }

    @property
    def url(self) -> str:
        """Get Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

class MQTTConfig(BaseSettings):
    """MQTT broker configuration"""

    host: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    keepalive: int = 60

    model_config = {
        "env_prefix": "MQTT_",
    }
```

### 3. Validation Functions

Common validation utilities:

```python
import re
from typing import Any

def validate_serial_number(serial: str) -> bool:
    """
    Validate instrument serial number format

    Args:
        serial: Serial number to validate

    Returns:
        True if valid, False otherwise
    """
    # Example: SN followed by 6-12 alphanumeric characters
    pattern = r'^SN[A-Z0-9]{6,12}$'
    return bool(re.match(pattern, serial))

def validate_ip_address(ip: str) -> bool:
    """
    Validate IPv4 address

    Args:
        ip: IP address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False

    # Check each octet is 0-255
    octets = ip.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    return filename[:255]
```

### 4. Constants and Enums

Shared constants:

```python
from enum import Enum

class InstrumentStatus(str, Enum):
    """Instrument status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    CALIBRATION = "calibration"
    RETIRED = "retired"

class MeasurementUnit(str, Enum):
    """Common measurement units"""
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KELVIN = "K"
    GRAM = "g"
    KILOGRAM = "kg"
    MILLIGRAM = "mg"
    LITER = "L"
    MILLILITER = "mL"
    MICROLITER = "µL"

# API Constants
API_VERSION = "v1"
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

# Time Constants
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 3600  # 1 hour
```

### 5. Utility Functions

General-purpose utilities:

```python
from datetime import datetime, timezone
from typing import Optional
import hashlib

def utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format)

def parse_datetime(dt_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime from string"""
    return datetime.strptime(dt_str, format)

def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using specified algorithm

    Args:
        text: Text to hash
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(text.encode('utf-8'))
    return hasher.hexdigest()

def truncate_string(text: str, length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to specified length

    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix
```

## Usage Examples

### Basic Model Usage

```python
from elims_common.models import BaseInstrument, BaseLocation

# Create instrument
instrument = BaseInstrument(
    name="UV-Vis Spectrophotometer",
    model="Lambda 365",
    serial_number="SN12345678",
    manufacturer="PerkinElmer",
    status="active",
)

# Validate and access data
print(instrument.name)  # UV-Vis Spectrophotometer
print(instrument.is_active())  # True

# Serialize to dict
data = instrument.model_dump()

# Serialize to JSON
json_str = instrument.model_dump_json()
```

### Configuration Management

```python
from elims_common.config import DatabaseConfig, CacheConfig, MQTTConfig

# Load from environment variables
db_config = DatabaseConfig()
print(db_config.url)  # mysql+pymysql://user:pass@host:3306/db

cache_config = CacheConfig()
print(cache_config.url)  # redis://:pass@host:6379/0

mqtt_config = MQTTConfig()
print(f"{mqtt_config.host}:{mqtt_config.port}")
```

### Validation

```python
from elims_common.validators import validate_serial_number, validate_ip_address

# Validate serial number
if validate_serial_number("SN12345678"):
    print("Valid serial number")

# Validate IP address
if validate_ip_address("192.168.1.1"):
    print("Valid IP address")
```

## Development

### Setup

```bash
# Navigate to package directory
cd packages/elims-common

# Install in development mode with dev dependencies
uv pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=elims_common --cov-report=html

# Run specific test
pytest tests/test_elims.py::test_function_name
```

### Code Quality

```bash
# Type checking
mypy elims_common

# Linting
ruff check elims_common

# Auto-fix issues
ruff check elims_common --fix

# Format code
ruff format elims_common
```

## Publishing

### Build Package

```bash
# Build wheel and sdist
python -m build
```

### Install Locally

```bash
# Install from wheel
pip install dist/elims_common-0.0.1-py3-none-any.whl
```

## API Reference

### Models

- `BaseInstrument`: Base model for instruments
- `BaseLocation`: Base model for locations
- `BaseMeasurement`: Base model for measurements
- `BaseUser`: Base model for users

### Configuration

- `DatabaseConfig`: Database connection settings
- `CacheConfig`: Redis cache settings
- `MQTTConfig`: MQTT broker settings

### Validators

- `validate_serial_number()`: Validate serial number format
- `validate_ip_address()`: Validate IPv4 address
- `sanitize_filename()`: Sanitize filename
- `validate_email()`: Validate email address

### Constants

- `InstrumentStatus`: Instrument status enum
- `MeasurementUnit`: Measurement unit enum
- `API_VERSION`: API version constant
- Cache TTL constants

### Utilities

- `utc_now()`: Get current UTC time
- `format_datetime()`: Format datetime to string
- `parse_datetime()`: Parse datetime from string
- `hash_string()`: Hash string
- `truncate_string()`: Truncate string

## Best Practices

1. **Type Hints**: Use type hints for all functions
1. **Validation**: Leverage Pydantic for data validation
1. **Immutability**: Prefer immutable data structures
1. **Documentation**: Document all public APIs
1. **Testing**: Maintain high test coverage (>80%)
1. **Versioning**: Follow semantic versioning

## Dependencies

### Core Dependencies

- `pydantic>=2.0.0`: Data validation
- `pydantic-settings>=2.0.0`: Settings management

### Development Dependencies

- `pytest>=7.4.0`: Testing framework
- `pytest-cov>=4.1.0`: Coverage reporting
- `pytest-asyncio>=0.21.0`: Async testing
- `ruff>=0.1.0`: Linting and formatting
- `mypy>=1.5.0`: Static type checking

## Contributing

1. Make changes in `elims_common/` directory
1. Add tests in `tests/` directory
1. Run tests: `pytest`
1. Check types: `mypy elims_common`
1. Format code: `ruff format elims_common`
1. Update version in `pyproject.toml`

## License

MIT License - see LICENSE file for details

## Related Documentation

- [Backend Documentation](../backend/index.md)
- [ELIMS Raspberry Package](../elims-raspberry/index.md)
- [API Documentation](../../api.md)
