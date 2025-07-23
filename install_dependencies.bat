@echo off
echo.
echo [100xFenok-generator] Dependency Installation Script
echo.

REM Check if virtual environment exists, create if not.
IF NOT EXIST .\venv\Scripts\activate (
    echo Virtual environment not found. Creating it now...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo Failed to create virtual environment. Please check your Python installation.
        pause
        exit /b
    )
    echo Virtual environment created successfully.
)

echo.
echo Activating virtual environment...
call .\venv\Scripts\activate

echo.
echo Upgrading pip...
python.exe -m pip install --upgrade pip

echo.
echo Installing required libraries from requirements.txt...
pip install -r requirements.txt

echo.
echo Installation complete.
echo.
pause