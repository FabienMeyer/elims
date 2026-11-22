# Runtime configuration

This directory contains version-controlled configuration mounted into infrastructure containers.

- `grafana/` provisions data sources and dashboards.
- `prometheus/` defines metric scrape targets.

Secrets and persistent runtime data do not belong here. Store secrets in `.env` or a production secret manager; Docker named volumes hold service data.
