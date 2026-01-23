# Deployment Workflows

## Overview

ELIMS uses two deployment workflows for different environments:

- **Staging**: Automatic deployment on every push to main
- **Production**: Manual deployment triggered by GitHub releases

Both workflows use Docker Compose and self-hosted runners.

## Deploy to Staging

### Workflow File

`deploy-staging.yml`

### Trigger

Automatically runs on push to `main` or `master` branches.

### Environment

- **Name**: staging
- **URL**: `https://dashboard.staging.${{ secrets.DOMAIN_STAGING }}`

### Requirements

- Self-hosted runner (can be labeled with 'staging')
- Docker and Docker Compose installed on runner
- Access to deployment server

### Steps

1. **Checkout Code**

   - Checks out the latest code from the repository

1. **Create .env File**

   - Generates environment configuration
   - Uses secrets from GitHub repository settings
   - Includes all required variables for services

1. **Build and Deploy**

   - Builds Docker images: `docker compose build`
   - Starts services: `docker compose up -d`

1. **Wait for Services**

   - Waits 30 seconds for services to initialize
   - Displays service status

1. **Health Check**

   - Verifies API is responding
   - Tests: `https://api.staging.${{ secrets.DOMAIN_STAGING }}/health`
   - Fails deployment if health check fails

### Required Secrets

Configure in: `Settings > Secrets and variables > Actions > Secrets`

#### Database Secrets

- `MARIADB_ROOT_PASSWORD`: MariaDB root password
- `MARIADB_DATABASE`: Database name (e.g., `elims`)
- `MARIADB_USER`: Database user (e.g., `elims`)
- `MARIADB_PASSWORD`: Database user password

#### Redis Secrets

- `REDIS_PASSWORD`: Redis authentication password

#### MQTT Secrets

- `MQTT_USERNAME`: MQTT broker username
- `MQTT_PASSWORD`: MQTT broker password

#### Backend Secrets

- `BACKEND_SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

#### Grafana Secrets

- `GRAFANA_ADMIN_USER`: Grafana admin username
- `GRAFANA_ADMIN_PASSWORD`: Grafana admin password

#### Domain Secrets

- `DOMAIN_STAGING`: Staging domain (e.g., `staging.example.com`)
- `STACK_NAME_STAGING`: Docker stack name (e.g., `elims-staging`)

### Environment Variables Set

The workflow creates a `.env` file with:

```env
# Database
MARIADB_ROOT_PASSWORD=***
MARIADB_DATABASE=elims
MARIADB_USER=elims
MARIADB_PASSWORD=***
MARIADB_HOST=mariadb
MARIADB_PORT=3306

# Redis
REDIS_PASSWORD=***
REDIS_HOST=redis
REDIS_PORT=6379

# MQTT
MQTT_HOST=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=***
MQTT_PASSWORD=***

# Backend
BACKEND_SECRET_KEY=***
BACKEND_ALGORITHM=HS256
BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=https://dashboard.staging.example.com,https://api.staging.example.com
ENVIRONMENT=staging

# Grafana
GRAFANA_ADMIN_USER=***
GRAFANA_ADMIN_PASSWORD=***

# Docker
DOMAIN=staging.example.com
STACK_NAME=elims-staging
```

## Deploy to Production

### Workflow File

`deploy-production.yml`

### Trigger

Manually triggered when a GitHub Release is published.

### Environment

- **Name**: production
- **URL**: `https://dashboard.${{ secrets.DOMAIN_PRODUCTION }}`

### Requirements

- Self-hosted runner (can be labeled with 'production')
- Docker and Docker Compose installed on runner
- Access to production server
- GitHub Release created

### Steps

Same as staging deployment, but with production-specific configuration:

1. **Checkout Code**
1. **Create .env File** (with production secrets)
1. **Build and Deploy**
1. **Wait for Services**
1. **Health Check**

### Required Secrets

Same categories as staging, but with `-production` suffixes:

- `MARIADB_ROOT_PASSWORD`
- `MARIADB_DATABASE`
- `MARIADB_USER`
- `MARIADB_PASSWORD`
- `REDIS_PASSWORD`
- `MQTT_USERNAME`
- `MQTT_PASSWORD`
- `BACKEND_SECRET_KEY`
- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`
- `DOMAIN_PRODUCTION`
- `STACK_NAME_PRODUCTION`

### Environment Variables Set

Similar to staging, but:

- `ENVIRONMENT=production`
- Uses production domain
- May have stricter CORS policies

## Self-Hosted Runners

### Setup

1. Go to: `Settings > Actions > Runners > New self-hosted runner`
1. Follow instructions for your OS
1. Add labels (optional): `staging`, `production`

### Requirements

- **Docker**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later
- **Network Access**: Ability to pull images and access GitHub
- **Disk Space**: Sufficient for Docker images and containers
- **Permissions**: User must be in docker group

### Installation Example (Ubuntu)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Download and configure runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
./config.sh --url https://github.com/FabienMeyer/elims --token YOUR_TOKEN

# Start runner as service
sudo ./svc.sh install
sudo ./svc.sh start
```

## Deployment Process

### Staging Deployment

1. Developer pushes to `main` branch
1. Tests run (backend, frontend, lint)
1. If tests pass, deployment workflow triggers
1. Runner builds and deploys to staging
1. Health check verifies deployment
1. Team reviews staging environment

### Production Deployment

1. Create a new release on GitHub:
   - Go to: `Releases > Create a new release`
   - Choose a tag (e.g., `v1.0.0`)
   - Fill in release notes
   - Publish release
1. Deployment workflow triggers automatically
1. Runner builds and deploys to production
1. Health check verifies deployment
1. Monitor production logs and metrics

## Health Checks

### API Health Endpoint

The workflows check: `/health`

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "mqtt": "connected"
}
```

### Troubleshooting Health Check Failures

1. **Check Service Status**

   ```bash
   docker compose ps
   ```

1. **View Service Logs**

   ```bash
   docker compose logs backend
   docker compose logs mariadb
   docker compose logs redis
   ```

1. **Test Health Endpoint Manually**

   ```bash
   curl https://api.staging.example.com/health
   ```

1. **Verify Environment Variables**

   ```bash
   docker compose config
   ```

## Rollback Procedure

### Staging Rollback

1. Revert the commit on `main` branch
1. Push the revert
1. Workflow will automatically deploy previous version

### Production Rollback

1. **Quick Rollback** (using previous images):

   ```bash
   # On production server
   docker compose down
   docker compose up -d
   ```

1. **Release Rollback**:

   - Delete the problematic release
   - Create a new release from previous stable tag
   - Workflow will deploy previous version

1. **Manual Rollback**:

   ```bash
   # On production server
   git checkout v1.0.0  # Previous stable version
   docker compose build
   docker compose up -d
   ```

## Monitoring Deployments

### Grafana Dashboards

Access observability at: `https://grafana.[staging|production].example.com`

Monitor:

- **Application Logs**: Loki dashboard
- **Container Metrics**: Docker container stats
- **API Response Times**: Application metrics
- **Error Rates**: HTTP status codes

### Log Access

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f backend

# View recent logs
docker compose logs --tail=100 backend
```

## Security Best Practices

1. **Secrets Management**

   - Never commit secrets to repository
   - Rotate secrets regularly
   - Use strong, unique passwords

1. **HTTPS/TLS**

   - Always use HTTPS in production
   - Configure Traefik with Let's Encrypt
   - Redirect HTTP to HTTPS

1. **Access Control**

   - Limit self-hosted runner access
   - Use environment protection rules
   - Require approvals for production

1. **Network Security**

   - Use internal Docker networks
   - Expose only necessary ports
   - Configure firewall rules

1. **Monitoring**

   - Set up alerts for failures
   - Monitor resource usage
   - Track deployment frequency

## Troubleshooting

### Deployment Fails

1. **Check Runner Status**

   - Verify runner is online and active
   - Check runner logs

1. **Check Secrets**

   - Verify all required secrets are configured
   - Ensure no typos in secret names

1. **Check Docker**

   - Verify Docker daemon is running
   - Check disk space: `df -h`
   - Check Docker logs: `journalctl -u docker`

### Service Won't Start

1. **Check Logs**

   ```bash
   docker compose logs service-name
   ```

1. **Check Dependencies**

   - Verify database is ready
   - Check Redis connection
   - Test MQTT broker

1. **Check Configuration**

   ```bash
   docker compose config
   ```

### Health Check Fails

1. **Wait Longer**

   - Increase wait time in workflow
   - Services may need more time to initialize

1. **Check Backend Logs**

   ```bash
   docker compose logs backend
   ```

1. **Test Manually**

   ```bash
   curl http://localhost:8000/health
   ```

## Related Workflows

- [Test Backend](test-backend.md) - Backend tests must pass
- [Test Frontend](test-frontend.md) - Frontend tests must pass
- [Test Docker Compose](test-docker-compose.md) - Integration tests
- [Latest Changes](latest-changes.md) - Release notes automation
