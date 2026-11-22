# Observability

The local stack includes Prometheus for metrics collection and Grafana for visualization.

## Start the stack

Copy `.env.example` to `.env`, replace `GRAFANA_ADMIN_PASSWORD`, and start the services:

```bash
docker compose up --build
```

- Grafana: <http://localhost:3000>
- Prometheus: <http://localhost:9090>
- Backend metrics: <http://localhost:8000/metrics>

Grafana automatically provisions the Prometheus data source and the **ELIMS backend overview** dashboard. Configuration is stored under `config/`; metric and dashboard data are stored in named Docker volumes.

With the Traefik overlay, Grafana is available through the host configured by `GRAFANA_DOMAIN`, which defaults to `grafana.localhost`.

## Production considerations

- Replace the default Grafana password before deployment.
- Do not expose Prometheus publicly unless access is authenticated and restricted.
- Protect Grafana with TLS and an identity provider or another suitable authentication layer.
- Adjust `PROMETHEUS_RETENTION` according to available storage and operational requirements.
