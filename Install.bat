@echo off
setlocal enabledelayedexpansion
:: Set variables to zero or null 
set VENV_DIR=.venv
:main
set wrong_version=0
set WinAliases=0
set python_path_exe=nul
set python_path_app=nul
cls
:: Checks if there is a preexisting virtual environment and prompts to remove it 
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
:: Find the location of the Python executable
for /f %%i in ('where python') do (
    set "python_path_check=%%i"
    !python_path_check! --version 2>nul
    if !errorlevel! EQU 9009 (
        set WinAliases=1
    ) else (
        !python_path_check! --version 2>NUL | findstr /R ."3.10". > NUL
        if !errorlevel! EQU 0 (
            echo !python_path_check! | findstr /R ."Python310". > NUL
            if !errorlevel! EQU 0 (
                set python_path_exe=!python_path_check!
            )
            echo !python_path_check! | findstr /R ."WindowsApps". > NUL
            if !errorlevel! EQU 0 ( 
                set python_path_app=!python_path_check!
            )
        ) else (
            set wrong_version=1
        )
    )
)
:: Set the default python to the stand alone version 
if NOT !python_path_exe! EQU nul (
    echo Using !python_path_exe! 
    set python_path=!python_path_exe!
) else if NOT !python_path_app! EQU nul (
    :: Ask the user if they would like to install the standalone version of python 
    :winask
    cls
    call:cecho cyan "It looks like you are running the Windows store version of python."
    call:cecho cyan "This version of python is known to run slower than the standalone version."
    echo [33m
    set /p "choice=Would you like to be directed to the install page? [Y/N]:"
    echo [0m
    set "choice=!choice:~0,1!"
    set "choice=!choice:~0,1!"
    if /i "!choice!"=="Y" (
        cls
        goto :install_python
    ) else if /i "!choice!"=="N" (
        echo You have chosen to continue with the Windows App store version of python.
        pause
    ) else (
        call:cecho red "Invalid choice. Please enter Y or N."
        goto :winask
    )
    set python_path=!python_path_app!
) else if !wrong_version! EQU 1 (
    goto wrong_python_display 
) else if !WinAliases! EQU 1 (
    goto wrong_python_display
)


:python_installed
call:cecho green "Python 3.10.x is installed and running."
:activate
:: Check the there is a existing virtual environment and it not creates one 
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
if !errorlevel! equ 0 (
    call:cecho green "Pip is up-to-date."
) else (
   call:cecho green "Pip has been upgraded to the latest version."
)
:: Installing requirements 

call:cecho yellow "This process could take a long time please be patient"
pause
pip install -r requirements.txt
:playwright_check
pip show playwright >nul 2>&1
if !errorlevel! equ 0 (
    call:cecho green "Playwright Dependencies installed."
) else (
    echo Installing Playwright Dependencies...
    python -m playwright install
    python -m playwright install-deps
    goto playwright_check
)

:again
echo [33m
set /p "choice=Do you want to run the install script again? [Y/N]:"
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

:exit
echo Press any key to Return to menu...
pause >nul
call run.bat
cmd /k


:wrong_python_display
echo [31mIt looks like python version 3.10.x is not installed. Please refer to the documentation for help.[0m
:install_python
call:cecho yellow "Control Click to open links in browser:"
echo Documentation: [34mhttps://reddit-video-maker-bot.netlify.app/docs/prerequisites[0m
echo Windows Store Python: [34mhttps://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5[0m
echo Python site: [32m(Recommended)[0m [34mhttps://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe[0m
goto again


EXIT /B !ERRORLEVEL!
:: "Function" That allows coloring of text with call:cecho Text_color "Text to be displayed"
:cecho
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