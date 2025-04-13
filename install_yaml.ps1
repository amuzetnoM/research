# PowerShell script to install YAML tools and handle shellcheck

Write-Host "Installing YAML tools..." -ForegroundColor Green

# Install chocolatey if not already installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey package manager..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

# Install shellcheck (not needed on Windows but installing to avoid errors)
Write-Host "Installing shellcheck..."
choco install shellcheck -y

# Install Python if not already installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python..."
    choco install python -y
    refreshenv
}

# Install YAML tools
Write-Host "Installing YAML Python packages..."
python -m pip install --upgrade pip
python -m pip install pyyaml yamllint

Write-Host "YAML installation completed successfully!" -ForegroundColor Green
Write-Host "You can now use YAML tools in your environment."
