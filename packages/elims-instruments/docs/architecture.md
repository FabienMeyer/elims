# Architecture

This package owns the instrument domain without depending on FastAPI, SQLModel, or a hardware SDK.

Persistence models, HTTP schemas, network transports, and hardware drivers remain in consuming applications or dedicated adapter packages.
