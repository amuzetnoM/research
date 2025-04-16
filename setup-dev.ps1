<#
.SYNOPSIS
    Sets up the development environment for the research project
.DESCRIPTION
    This script installs and configures all required tools and dependencies
    for the research development environment, including Node.js, Python, and
    necessary frameworks.
#>

# Configuration
$ProjectRoot = "c:\_worxpace\research"
$FrontendPath = Join-Path $ProjectRoot "frontend"
$Head1Path = Join-Path $ProjectRoot "head_1"
$NodeInstallerPath = Join-Path $FrontendPath "node-installer.msi"

# Check for admin privileges
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($user)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Request admin if not running as admin
if (-not (Test-Administrator)) {
    Write-Host "This script requires administrator privileges. Restarting as admin..." -ForegroundColor Yellow
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Create project directories
function Ensure-DirectoryStructure {
    Write-Host "Setting up directory structure..." -ForegroundColor Cyan
    
    $Directories = @(
        $ProjectRoot,
        $FrontendPath,
        (Join-Path $ProjectRoot "head_1"),
        (Join-Path $ProjectRoot "head_1\system"),
        (Join-Path $ProjectRoot "head_1\terminal_1"),
        (Join-Path $ProjectRoot "head_1\terminal_2"),
        (Join-Path $ProjectRoot "head_1\frameworks"),
        (Join-Path $ProjectRoot "head_1\frameworks\_system\_deployment")
    )

    foreach ($Directory in $Directories) {
        if (-not (Test-Path $Directory)) {
            Write-Host "  Creating directory: $Directory"
            New-Item -ItemType Directory -Path $Directory -Force | Out-Null
        }
    }
}

# Install Node.js
function Install-NodeJS {
    Write-Host "Installing Node.js..." -ForegroundColor Cyan
    
    if (Test-Path $NodeInstallerPath) {
        Write-Host "  Running Node.js installer..."
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$NodeInstallerPath`" /quiet" -Wait
        
        # Update PATH for current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        
        # Setup environment with nodevars
        $NodeVarsPath = Join-Path $FrontendPath "nodevars.bat"
        if (Test-Path $NodeVarsPath) {
            Write-Host "  Configuring Node.js environment variables..."
            $TempFile = [System.IO.Path]::GetTempFileName()
            cmd.exe /c "`"$NodeVarsPath`" && set > `"$TempFile`""
            Get-Content $TempFile | ForEach-Object {
                if ($_ -match "^(.*?)=(.*)$") {
                    Set-Item -Path "env:$($matches[1])" -Value $matches[2]
                }
            }
            Remove-Item $TempFile
        }
    } else {
        Write-Host "  Node.js installer not found at $NodeInstallerPath" -ForegroundColor Red
        Write-Host "  Please ensure the installer exists or run the full system setup" -ForegroundColor Yellow
    }
}

# Setup frontend development environment
function Setup-Frontend {
    Write-Host "Setting up frontend development environment..." -ForegroundColor Cyan
    
    if (Get-Command node -ErrorAction SilentlyContinue) {
        Push-Location $FrontendPath
        
        # Initialize npm project if needed
        if (-not (Test-Path "package.json")) {
            Write-Host "  Initializing npm project..."
            npm init -y
        }
        
        # Install basic dependencies
        Write-Host "  Installing frontend dependencies..."
        npm install --save react react-dom
        npm install --save-dev webpack webpack-cli babel-loader @babel/core @babel/preset-env @babel/preset-react
        
        Pop-Location
    } else {
        Write-Host "  Node.js not available. Skipping frontend setup." -ForegroundColor Yellow
    }
}

# Setup Python environment
function Setup-PythonEnvironment {
    Write-Host "Setting up Python environment..." -ForegroundColor Cyan
    
    # Run install_tools.bat if it exists to ensure Python and VS tools are installed
    $InstallToolsPath = Join-Path $FrontendPath "install_tools.bat"
    if (Test-Path $InstallToolsPath) {
        Write-Host "  Running tools installer script..."
        Start-Process -FilePath $InstallToolsPath -Wait
    }
    
    # Create and activate virtual environment
    $VenvPath = Join-Path $ProjectRoot "venv"
    if (-not (Test-Path $VenvPath)) {
        Write-Host "  Creating virtual environment..."
        python -m venv $VenvPath
    }
    
    # Install Python packages
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        Write-Host "  Installing Python packages..."
        & $ActivateScript
        
        pip install --upgrade pip
        pip install numpy matplotlib pandas scikit-learn psutil
        
        # Optional ML packages
        try {
            pip install torch torchvision
        } catch {
            Write-Host "  PyTorch installation failed, continuing without it" -ForegroundColor Yellow
        }
        
        try {
            pip install tensorflow
        } catch {
            Write-Host "  TensorFlow installation failed, continuing without it" -ForegroundColor Yellow
        }
        
        try {
            pip install transformers
        } catch {
            Write-Host "  Transformers installation failed, continuing without it" -ForegroundColor Yellow
        }
        
        # Deactivate virtual environment
        deactivate
    }
}

# Setup AI frameworks
function Setup-Frameworks {
    Write-Host "Setting up AI frameworks..." -ForegroundColor Cyan
    
    $FrameworkSetupPath = Join-Path $Head1Path "frameworks\_system\_deployment\setup_frameworks.sh"
    if (Test-Path $FrameworkSetupPath) {
        Write-Host "  Framework setup script found, will be executed later during system setup"
    } else {
        Write-Host "  Creating basic framework setup script..."
        $FrameworkSetupDir = Split-Path $FrameworkSetupPath -Parent
        
        if (-not (Test-Path $FrameworkSetupDir)) {
            New-Item -ItemType Directory -Path $FrameworkSetupDir -Force | Out-Null
        }
        
        @"
#!/bin/bash
set -e

SCRIPT_DIR="`$( cd "`$( dirname "`${BASH_SOURCE[0]}" )" && pwd )"
echo "Setting up AI Frameworks in `$SCRIPT_DIR"

# Create necessary directories
mkdir -p "`$SCRIPT_DIR/data/models/self_awareness"
mkdir -p "`$SCRIPT_DIR/data/models/edf"
mkdir -p "`$SCRIPT_DIR/data/lexicons"
mkdir -p "`$SCRIPT_DIR/data/config"

# Install Python dependencies will be handled by the main setup script

echo "Setup complete. AI Frameworks are ready to use."
echo "To enable the frameworks, set ENABLE_SELF_AWARENESS=true and ENABLE_EMOTIONAL_FRAMEWORK=true in your environment."
"@ | Set-Content -Path $FrameworkSetupPath -Encoding UTF8
    }
}

# Create a launcher script
function Create-LauncherScript {
    Write-Host "Creating launcher script..." -ForegroundColor Cyan
    
    $RunCmdPath = Join-Path $ProjectRoot "run.cmd"
    if (-not (Test-Path $RunCmdPath)) {
        @"
@echo off
REM Launcher script for the research environment

echo Starting research environment...

REM Set up Node.js environment
call "%~dp0frontend\nodevars.bat"

REM Activate Python environment
call "%~dp0venv\Scripts\activate.bat"

REM Start the environment
cd "%~dp0"
cmd /k echo Research environment is ready. Type 'exit' to close.
"@ | Set-Content -Path $RunCmdPath -Encoding ASCII
        
        Write-Host "  Created launcher script at $RunCmdPath"
    }
}

# Main function
function Main {
    $startTime = Get-Date
    
    Write-Host "=== Starting Development Environment Setup ===" -ForegroundColor Green
    
    Ensure-DirectoryStructure
    Install-NodeJS
    Setup-Frontend
    Setup-PythonEnvironment
    Setup-Frameworks
    Create-LauncherScript
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
    Write-Host "Setup completed in $([math]::Round($duration / 60, 2)) minutes." -ForegroundColor Green
    Write-Host "`nNext Steps:"
    Write-Host "1. Start the environment using:"
    Write-Host "   > cd $ProjectRoot"
    Write-Host "   > .\run.cmd"
    Write-Host "2. For a full system setup, run:"
    Write-Host "   > cd $ProjectRoot\setup"
    Write-Host "   > python system_setup.py"
}

# Run the script
Main
