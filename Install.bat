@echo off
setlocal enabledelayedexpansion
set VENV_DIR=.venv
set "requirements_file=requirements.txt"
:main
cls
:: Check if Python version 3.10.x is installed and create/activate a virtual environment.
python --version 2>NUL | findstr /R "3.10" > NUL
if %errorlevel% NEQ 0 (
    powershell write-host -fore Red  It looks like python version 3.10.x isn't installed. Please refer to the documentation for help.
    powershell write-host -fore Red  https://reddit-video-maker-bot.netlify.app/docs/prerequisites
) else (
    powershell write-host -fore Green Python 3.10 is installed and running.
    :activate
    if exist "%VENV_DIR%" (  
        echo Activating virtual environment...
        call "%VENV_DIR%\Scripts\activate.bat"
    ) else (
        echo Creating virtual environment...
        python -m venv %VENV_DIR%
        goto activate
    )
    python.exe -m pip install --upgrade pip >NUL
    if %errorlevel% equ 0 (
        powershell write-host -fore Green Pip is up-to-date.
    ) else (
        powershell write-host -fore Green Pip has been upgraded to the latest version.
    )
    :: Check if requirements.txt exists
    if not exist %requirements_file% (
        powershell write-host -fore Red %requirements_file% does not exist.
        exit /b 1
    )
    :: Loop through each line in requirements.txt and check if the package is installed
    echo Checking dependencies...
    for /f "tokens=1 delims=~=" %%a in (%requirements_file%) do (
        pip show %%a >nul 2>&1
        if errorlevel 1 (
            powershell write-host -fore Red %%a is not installed.
            set "missing=1"
        )
    )
    :: Check if any packages are missing
    if defined missing (
        powershell write-host -fore Yellow One or more required packages are missing.
        :ask_for_choice
        powershell write-host -fore Yellow Do you want to install them? [Y/N]:
        set /p choice=
        set "choice=!choice:~0,1!"
        set "choice=!choice:~0,1!"
        if /i "!choice!"=="Y" (
            pip install -r "%requirements_file%"
            if errorlevel 1 (
                powershell write-host -fore Red Installation failed.
                goto :ask_for_choice
            ) else (
                powershell write-host -fore Green Installation successful.
            )
        ) else if /i "!choice!"=="N" (
            echo You chose not to install missing packages.
            goto again
        ) else (
            powershell write-host -fore Red Invalid choice. Please enter Y or N.
            goto :ask_for_choice
        )
    ) else (
        powershell write-host -fore Green All required packages are installed.
    )
    :playwright_check
    pip show playwright >nul 2>&1
    if %errorlevel% equ 0 (
        powershell write-host -fore Green Playwright is installed.
    ) else (
        echo Installing Playwright...
        python -m playwright install
        python -m playwright install-deps
        goto playwright_check
    )
    :runbot?
    powershell write-host -fore Yellow Would you like to run the bot now? [Y/N]:
    set /p choice=
    set "choice=!choice:~0,1!"
    set "choice=!choice:~0,1!"
    if /i "!choice!"=="Y" (
        call run.bat
        goto :exit
    ) else if /i "!choice!"=="N" (
        goto :again
    ) else (
        powershell write-host -fore Red Invalid choice. Please enter Y or N.
        goto :runbot?
    )
)
:again
powershell write-host -fore Yellow Do you want to run the script again? [Y/N]:
set /p choice=
set "choice=!choice:~0,1!"
set "choice=!choice:~0,1!"
if /i "!choice!"=="Y" (
    goto :main
) else if /i "!choice!"=="N" (
    goto :exit
) else (
    powershell write-host -fore Red Invalid choice. Please enter Y or N.
    goto :again
)
endlocal
:exit
echo Press any key to exit ...
pause >nul