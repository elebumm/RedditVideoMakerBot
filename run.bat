@echo off
set VENV_DIR=.venv
setlocal enabledelayedexpansion
:menu
cls
echo [34m########[0m [36mMENU[0m [34m########[0m
echo 1. [32mInstall[0m
echo 2. [32mRun[0m
echo 3. [32mOpen CMD (.vevn)[0m
echo 4. [32mLaunch Web GUI [0m
echo [34m######################[0m
echo [33m
set /p "choice=Please make a selection :"
echo [0m
    if /i "!choice!"=="1" (
        call install.bat
    ) else if /i "!choice!"=="2" (
        goto run
    ) else if /i "!choice!"=="3" (
        if exist "%VENV_DIR%" ( 
            cls
            echo Activating virtual environment...
            call "%VENV_DIR%\Scripts\activate.bat"
            cmd /k
        ) else (
            cls
            call:cecho red "No virtual environment detected"
            call:cecho red "Please select Install from the menu"
            pause 
            goto menu
        )
    ) else if /i "!choice!"=="4" (
        if exist "%VENV_DIR%" (
            echo Activating virtual environment...
            call "%VENV_DIR%\Scripts\activate.bat"
            echo Launching Web Graphical User Interface 
            start python GUI.py
        ) else (
            cls
            call:cecho red "No virtual environment detected"
            call:cecho red "Please select Install from the menu"
            pause 
            goto menu
        )
    )else (
        cls
        goto menu
    )
goto:menu    
:run
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
    :again
    cls
    call:cecho yellow "It does not look like the prerequisites for the bot had been installed."
    echo [33m
    set /p "choice=Would you like to do that now? [Y/N]:"
    echo [0m
    set "choice=!choice:~0,1!"
    set "choice=!choice:~0,1!"
    if /i "!choice!"=="Y" (
        call install.bat
    ) else if /i "!choice!"=="N" (
        exit
    ) else (
        cls
        call:cecho red "Invalid choice. Please enter Y or N."
        goto :again
    )
)
endlocal


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


EXIT /B %ERRORLEVEL%
:venv
if exist "%VENV_DIR%" (
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
EXIT /B 0