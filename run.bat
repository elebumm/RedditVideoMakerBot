@echo off
set VENV_DIR=.venv

if exist "%VENV_DIR%" (
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
    echo Running Python script...
    python main.py
    if errorlevel 1 (
        echo An error occurred. Press any key to exit.
        pause >nul
        exit
    )

) else (
    setlocal enabledelayedexpansion
    :again
    powershell write-host -fore Yellow It does not look like the prerequisites for the bot had been installed.
    powershell write-host -fore Yellow Would you like to do that now? [Y/N]:
    set /p choice=
    set "choice=!choice:~0,1!"
    set "choice=!choice:~0,1!"
    if /i "!choice!"=="Y" (
        call install.bat
    ) else if /i "!choice!"=="N" (
        exit
    ) else (
        cls
        powershell write-host -fore Red Invalid choice. Please enter Y or N.
        goto :again
    )
    endlocal
)
