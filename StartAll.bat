cd C:\Users\JAdmin\Desktop\RYBot

@echo off
set VENV_DIR=.venv

if exist "%VENV_DIR%" (
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
)

echo Running Python script...
python main.py
python upload.py

if errorlevel 1 (
    echo An error occurred. Press any key to exit.
    pause >nul
)
