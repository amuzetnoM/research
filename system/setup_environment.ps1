# PowerShell version of setup_environment.sh
Write-Host "Setting up Python environment..."
python (Join-Path (Get-Location) "..\setup.py")

# Check Docker installation
$dockerInstalled = $null -ne (Get-Command "docker" -ErrorAction SilentlyContinue)
if (-not $dockerInstalled) {
    $installDocker = Read-Host "Docker not found. Would you like to install Docker? (y/n)"
    if ($installDocker -eq "y") {
        Write-Host "Installing Docker..."
        Write-Host "Please download Docker Desktop for Windows from https://www.docker.com/products/docker-desktop"
        Start-Process "https://www.docker.com/products/docker-desktop"
    }
}

# Check NVIDIA GPU availability
$gpuAvailable = $false
try {
    $null = & nvidia-smi
    $gpuAvailable = $true
}
catch {
    $gpuAvailable = $false
}

if ($gpuAvailable) {
    Write-Host "NVIDIA GPU detected."
    
    # Check if NVIDIA Docker support is installed
    $nvidiaDockerInstalled = $false
    try {
        $dockerInfo = docker info
        $nvidiaDockerInstalled = $dockerInfo -match "nvidia-container-toolkit"
    }
    catch {
        $nvidiaDockerInstalled = $false
    }
    
    if (-not $nvidiaDockerInstalled) {
        $installNvidia = Read-Host "NVIDIA Docker support not found. Would you like to install NVIDIA Container Toolkit? (y/n)"
        if ($installNvidia -eq "y") {
            Write-Host "Installing NVIDIA Container Toolkit..."
            Write-Host "Please follow the instructions at: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker"
            Start-Process "https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker"
        }
    }
    else {
        Write-Host "NVIDIA Docker support already installed."
    }
}

Write-Host "Environment setup complete."
Write-Host "To build and run the Docker container, use: ..\run.ps1"
