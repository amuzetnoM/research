# Check if Docker Desktop is running
$dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Write-Host "Docker Desktop is not running. Starting Docker Desktop..." -ForegroundColor Yellow
    # Ensure the path is correct for your system
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    # Wait for Docker daemon to likely be ready
    Write-Host "Waiting for Docker to initialize (approx. 30 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
} else {
    Write-Host "Docker Desktop is running." -ForegroundColor Green
}

# Verify Docker is responsive
docker version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker command failed. Please ensure Docker Desktop is running and responsive."
    exit 1
}

# Navigate to the script's directory to ensure docker-compose finds the .env file
Push-Location $PSScriptRoot

# Stop any existing containers defined in the compose file
Write-Host "Stopping any existing services defined in docker-compose.yml..." -ForegroundColor Cyan
docker-compose down
if ($LASTEXITCODE -ne 0) {
    Write-Warning "docker-compose down failed. Continuing..."
}

# Start the containers using the .env file for configuration
Write-Host "Starting containers with settings from docker-compose.yml and .env file..." -ForegroundColor Green
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Error "docker-compose up failed. Please check the logs."
    Pop-Location
    exit 1
}

# Check container health (basic check, more specific checks might be needed)
Write-Host "Checking container status (wait a few seconds for startup)..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
docker ps -a

# Display access information (retrieve token from environment, as compose sets it)
$jupyterToken = (docker-compose exec research_2 printenv JUPYTER_TOKEN).Trim()
# Use default from .env if exec fails (e.g., container starting up)
if (-not $jupyterToken) {
    # Basic parsing of .env, assumes simple KEY=VALUE format
    $envFileContent = Get-Content .\.env -Raw
    $envVars = $envFileContent | ConvertFrom-StringData -Delimiter '='
    $jupyterToken = $envVars.JUPYTER_TOKEN + " (from .env, container check failed)"
}

Write-Host "`nServices are starting up." -ForegroundColor Green
Write-Host "Access JupyterLab at: http://localhost:8889 (Token: $jupyterToken)" -ForegroundColor Cyan
Write-Host "Access Grafana at: http://localhost:3001 (Credentials in .env)" -ForegroundColor Cyan
Write-Host "Access Prometheus at: http://localhost:9091" -ForegroundColor Cyan

Pop-Location