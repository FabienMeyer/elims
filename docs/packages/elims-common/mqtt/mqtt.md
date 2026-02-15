# MQTT Broker Configuration Guide

## Overview

The ELIMS system uses **Eclipse Mosquitto 2.0** with:

- **TLS/SSL encryption** on port 8883
- **Username/password authentication**
- **ACL (Access Control Lists)** for fine-grained permissions
- **Self-signed certificates** for development (can be replaced with CA-signed in production)

## Current Users

### Backend Service

- **Username:** `fastapi`
- **Password:** `SecurePassword123!_FastAPI` (update in `.env`)
- **Permissions:** Read/write all topics under `devices/#`
- **Uses:** TLS with client certificates

### Raspberry Pi (Publisher)

- **Username:** `raspberry-01`
- **Password:** Hashed in `passwd` file
- **Permissions:** Publish telemetry and status to `devices/raspberry-01/telemetry` and `devices/raspberry-01/status`
- **Subscribes to:** `devices/raspberry-01/config` and `devices/raspberry-01/command`

## Adding a New Raspberry Pi Device

### Step 1: Generate Device-Specific Credentials

Inside the docker container or on the host with mosquitto-clients installed:

```bash
# Generate password hash for new device
mosquitto_passwd -b /mosquitto/config/passwd raspberry-02 your_secure_password_here
```

Or do it interactively:

```bash
mosquitto_passwd /mosquitto/config/passwd raspberry-02
# Enter password when prompted (twice)
```

### Step 2: Add ACL Rules

Edit `config/mosquitto/acl` and add rules for the new device:

```
# Device: Raspberry Pi 02
pattern write devices/raspberry-02/telemetry
pattern write devices/raspberry-02/status
pattern read devices/raspberry-02/config
pattern read devices/raspberry-02/command
```

### Step 3: Reload Mosquitto Configuration

If mosquitto is running in Docker:

```bash
docker compose exec mosquitto mosquitto_ctrl reload
```

Or restart the service:

```bash
docker compose restart mosquitto
```

## Certificates and TLS

### Certificate Files Location

```
config/mosquitto/certs/
├── ca.crt          # CA certificate (public, used by clients)
├── ca.key          # CA key (private, for signing)
├── ca.srl          # CA serial number tracking
├── server.crt      # Server certificate (public)
├── server.key      # Server key (private)
├── server.csr      # Server CSR (for renewals)
├── server.ext      # Server extensions
├── client.crt      # Client certificate (public)
├── client.csr      # Client CSR
└── client.key      # Client key (private)
```

### Connecting to MQTT with TLS

**Python Example (Backend):**

```python
from paho.mqtt.client import Client
import ssl

client = Client(client_id="my-device")
client.username_pw_set("fastapi", "SecurePassword123!_FastAPI")

# TLS Setup
tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
tls_context.check_hostname = False
tls_context.verify_mode = ssl.CERT_NONE  # Or use CERT_REQUIRED with proper verification
client.tls_set_context(tls_context)

client.connect("mosquitto", 8883, keepalive=60)
client.loop_forever()
```

**Mosquitto CLI Example:**

```bash
# Subscribe to telemetry
mosquitto_sub -h mosquitto -p 8883 \
  -u fastapi -P "SecurePassword123!_FastAPI" \
  --cafile config/mosquitto/certs/ca.crt \
  -t "devices/+/telemetry"

# Publish a test message
mosquitto_pub -h mosquitto -p 8883 \
  -u raspberry-01 -P "raspberry_password" \
  --cafile config/mosquitto/certs/ca.crt \
  -t "devices/raspberry-01/telemetry" \
  -m '{"temperature": 22.5, "timestamp": 1707487800}'
```

## ELIMS Publisher API

The backend provides a Python API for publishing configurations to devices:

```python
from app.mqtt.publisher import get_publisher

# Create publisher
publisher = get_publisher()

# Send configuration to device
publisher.publish_device_config("raspberry-01", {
    "sample_rate": 5,
    "enabled": True,
    "sensors": ["temperature", "humidity", "pressure"]
})

# Send firmware update notification
publisher.publish_firmware_update(
    "raspberry-01",
    "https://updates.example.com/firmware/v1.2.3.bin",
    checksum="abc123def456..."
)

# Send generic command
publisher.publish_command("raspberry-01", "reboot", {
    "delay_seconds": 10
})

publisher.disconnect()
```

## Topic Structure

### Sensor Data (Published by Raspberry: Pi)

```
devices/{device_id}/telemetry  → JSON with temperature, timestamp
devices/{device_id}/status     → JSON with device status
```

Example:

```json
{
  "temperature": 22.5,
  "timestamp": 1707487800,
  "humidity": 45.2,
  "pressure": 1013.25
}
```

### Control (Published by Backend/FastAPI)

```
devices/{device_id}/config     → Configuration updates
devices/{device_id}/command    → Commands to execute
devices/{device_id}/firmware   → Firmware update notifications
```

## Troubleshooting

### Connection Issues

**Check if mosquitto is running:**

```bash
docker compose ps mosquitto
```

**View mosquitto logs:**

```bash
docker compose logs mosquitto
```

**Test connectivity (plaintext, for debugging only):**

```bash
docker run -it --network elims-network eclipse-mosquitto mosquitto_sub \
  -h mosquitto -p 8883 -t '$SYS/#'
```

### Authentication Issues

**Verify user exists in passwd file:**

```bash
docker compose exec mosquitto cat /mosquitto/config/passwd
```

**Regenerate password hash:**

```bash
docker compose exec mosquitto mosquitto_passwd -b /mosquitto/config/passwd username newpassword
```

**Check ACL configuration:**

```bash
docker compose exec mosquitto cat /mosquitto/config/acl
```

### TLS Certificate Issues

**View certificate details:**

```bash
openssl x509 -in config/mosquitto/certs/server.crt -text -noout
openssl x509 -in config/mosquitto/certs/client.crt -text -noout
```

**Verify certificate and key match:**

```bash
openssl x509 -noout -modulus -in config/mosquitto/certs/server.crt | openssl md5
openssl rsa -noout -modulus -in config/mosquitto/certs/server.key | openssl md5
```

## Environment Variables

Configure in `.env`:

```env
# MQTT Connection
MQTT_HOST=mosquitto              # Broker hostname
MQTT_PORT=8883                   # TLS port
MQTT_USERNAME=fastapi            # Service username
MQTT_PASSWORD=SecurePassword123!_FastAPI  # Service password

# TLS/SSL Certificates (paths in Docker container)
MQTT_CERTIFICATE_AUTHORITY_FILE=config/mosquitto/certs/ca.crt
MQTT_CERTIFICATE_FILE=config/mosquitto/certs/client.crt
MQTT_KEY_FILE=config/mosquitto/certs/client.key
```

## Security Considerations

1. **Development vs Production:**

   - Development: Self-signed certificates (currently configured)
   - Production: Use CA-signed certificates from Let's Encrypt or similar

1. **Password Management:**

   - Change default passwords in production
   - Use strong, unique passwords per device
   - Rotate passwords periodically
   - Store passwords securely (not in version control)

1. **Network Security:**

   - Use TLS/SSL (port 8883) - never plaintext (8883) in production
   - Restrict MQTT broker access to trusted networks
   - Implement network-level firewall rules
   - Use VPN for remote access

1. **Access Control:**

   - Review ACL rules regularly
   - Principle of least privilege: only grant necessary permissions
   - Disable unused users
   - Audit connection logs

## Production Checklist

- [ ] Replace self-signed certificates with CA-signed certificates
- [ ] Change all default passwords
- [ ] Review and update ACL rules for all devices
- [ ] Enable persistent message storage (already enabled)
- [ ] Configure backup and restore procedures
- [ ] Set up monitoring and alerting for broker health
- [ ] Enable audit logging
- [ ] Test disaster recovery procedures
- [ ] Document all device passwords and credentials (in secure vault)
- [ ] Set up firewall rules to restrict MQTT access

## Useful Commands

```bash
# Reload configuration without restarting
docker compose exec mosquitto mosquitto_ctrl reload

# View current broker stats
docker compose exec mosquitto mosquitto_ctrl stats

# Restart mosquitto service
docker compose restart mosquitto

# View all subscribers
mosquitto_sub -h mosquitto -p 8883 \
  -u fastapi -P "SecurePassword123!_FastAPI" \
  --cafile config/mosquitto/certs/ca.crt \
  -t "$SYS/#"
```

## References

- [Eclipse Mosquitto Documentation](https://mosquitto.org/documentation/)
- [MQTT Specification](https://mqtt.org/)
- [OpenSSL Certificate Commands](https://www.openssl.org/)
