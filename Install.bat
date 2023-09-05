@echo off
setlocal enabledelayedexpansion
set VENV_DIR=.venv
set "requirements_file=requirements.txt"
:main
set "wrong_python=0"
cls
if exist "%VENV_DIR%" (
    call:cecho red "Previous virtual environment detected. May cause issues if not deleted."
    echo [33m
    set /p "choice=Would you like to remove this virtual environment? [Y/N]:"
    echo [0m
    set "choice=!choice:~0,1!"
    set "choice=!choice:~0,1!"
    if /i "!choice!"=="Y" (
         rmdir /s /q %VENV_DIR%
    ) else if /i "!choice!"=="N" (
        call:cecho red "You have chosen not to remove the current virtual environment. Please note this may cause issues with the installation."
    ) else (
        call:cecho red "Invalid choice. Please enter Y or N."
        goto :again
    )
)
cls
python --version >nul 2>&1
if %errorlevel% EQU 0 (
    :: Find the location of the Python executable
    for /f %%i in ('where python') do (
        set "python_path_check=%%i"
        echo !python_path_check!
        !python_path_check! --version 2>NUL | findstr /R "3.10" > NUL
        if %errorlevel% EQU 0 (
            echo python_path_check | findstr /R "Python310" > NUL
            if %errorlevel% EQU 0 (
                set "standalone=!python_path_check!"
            )
            echo python_path_check | findstr /R "WindowsApps" > NUL
            if %errorlevel% EQU 0 (
                set "WindowsApps=!python_path_check!"
            )
        ) else (
            set "wrong_python=1"
        )
    )
    if NOT "!standalone!"=="" (
        echo Using standalone Python
        set "python_path=!standalone!"
        goto python310
    ) else if NOT "!WindowsApps!"=="" (
        echo Using WindowsStore Python
        set "python_path=!WindowsApps!"
        goto python310
    ) 
    if !wrong_python! EQU 1 (
        goto wrong_python_display
    )
) else (
    goto wrong_python_display
)
:python310
call:cecho green "Python 3.10.x is installed and running."
:activate
if exist "%VENV_DIR%" (  
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo Creating virtual environment...
    !python_path! -m venv %VENV_DIR%
    goto activate
)
:: Upgrading pip  
python -m pip install --upgrade pip >NUL
if %errorlevel% equ 0 (
    call:cecho green "Pip is up-to-date."
) else (
   call:cecho green "Pip has been upgraded to the latest version."
)
:: Check if requirements.txt exists
if not exist %requirements_file% (
    call:cecho red "%requirements_file% does not exist."
    exit /b 1
)
:: Loop through each line in requirements.txt and check if the package is installed
echo Checking dependencies...
for /f "tokens=1 delims=~=" %%a in (%requirements_file%) do (
    pip show %%a >nul 2>&1
    if errorlevel 1 (
        call:cecho red "%%a is not installed."
        ::echo [31m%%a is not installed.[0m
        set "missing=1"
    )
)
:: Check if any packages are missing
if defined missing (
    call:cecho yellow "One or more required packages are missing."
    :ask_for_choice
    echo [33m
    set /p "choice=Do you want to install them? [Y/N]:"
    echo [0m
    set "choice=!choice:~0,1!"
    set "choice=!choice:~0,1!"
    if /i "!choice!"=="Y" (
        pip install -r "%requirements_file%"
        if errorlevel 1 (
            call:cecho red "Installation failed."
            goto :ask_for_choice
        ) else (
            call:cecho green "Installation successful."
        )
    ) else if /i "!choice!"=="N" (
        echo You chose not to install missing packages.
        goto again
    ) else (
        call:cecho red "Invalid choice. Please enter Y or N."
        goto :ask_for_choice
    )
) else (
    call:cecho green "All required packages are installed."
)
:playwright_check
pip show playwright >nul 2>&1
if %errorlevel% equ 0 (
    call:cecho green "Playwright is installed."
) else (
    echo Installing Playwright...
    python -m playwright install
    python -m playwright install-deps
    goto playwright_check
)
:runbot?
echo [33m
set /p "choice=Would you like to run the bot now? [Y/N]:"
echo [0m
set "choice=!choice:~0,1!"
set "choice=!choice:~0,1!"
if /i "!choice!"=="Y" (
    call run.bat
    goto :exit
) else if /i "!choice!"=="N" (
    goto :again
) else (
    call:cecho red "Invalid choice. Please enter Y or N."
    goto :runbot?
)
:again
echo [33m
set /p "choice=Do you want to run the script again? [Y/N]:"
echo [0m
set "choice=!choice:~0,1!"
set "choice=!choice:~0,1!"
if /i "!choice!"=="Y" (
    goto :main
) else if /i "!choice!"=="N" (
    goto :exit
) else (
    call:cecho red "Invalid choice. Please enter Y or N."
    goto :again
)
endlocal
:exit
echo Press any key to Return to menu...
pause >nul
call run.bat
cmd /k


:wrong_python_display
call:cecho red "It looks like python version 3.10.x is not installed. Please refer to the documentation for help."
call:cecho red "https://reddit-video-maker-bot.netlify.app/docs/prerequisites"
call:cecho yellow "Control Click to install Python: https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5"
goto again


EXIT /B %ERRORLEVEL%
:cecho
setlocal enabledelayedexpansion
set "color=%~1"
set "text=%~2"
if !color! == red (
    set "colored_text=[31m%text%[0m"
)
if !color! == green (
    set "colored_text=[32m%text%[0m"
)
if !color! == yellow (
    set "colored_text=[33m%text%[0m"
)
if !color! == blue (
    set "colored_text=[34m%text%[0m"
)
if !color! == magenta (
    set "colored_text=[35m%text%[0m"
)
if !color! == cyan (
    set "colored_text=[36m%text%[0m"
)
echo !colored_text!
endlocal
EXIT /B 0