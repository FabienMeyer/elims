# Load environment variables from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

# Override MQTT_HOST for local development (Docker uses 'mosquitto', local uses 'localhost')
$env:MQTT_HOST = "localhost"

Write-Host "Starting MQTT Subscriber with environment variables:" -ForegroundColor Green
Write-Host "  MQTT_HOST: $env:MQTT_HOST"
Write-Host "  MQTT_PORT: $env:MQTT_PORT"
Write-Host "  MQTT_USERNAME: $env:MQTT_USERNAME"
Write-Host ""

# Run the subscriber
python backend/app/mqtt/subscriber.py
