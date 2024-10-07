@echo off

if "%VIRTUAL_ENV%"=="" (
    echo Activating virtual environment...
    
    if not exist "env\Scripts\activate.bat" (
        echo Virtual environment not found!
        exit /b 1
    )

    call env\Scripts\activate.bat
) else (
    echo Already in a virtual environment: %VIRTUAL_ENV%
)

if not exist "runtime\startclient.py" (
    echo Python script not found!
    exit /b 1
)

python runtime\startclient.py %*
