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
