@echo off
echo.
echo [100xFenok-generator] Dependency Installation Script
echo.

REM Check if virtual environment exists
IF NOT EXIST .\venv\Scripts\activate (
    echo Error: Virtual environment not found.
    echo Please run 'python -m venv venv' first to create it.
    echo.
    pause
    exit /b
)

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
