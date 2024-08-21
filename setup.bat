@echo off
echo Setting up WhatsApp Automation Tool...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.7 or later and run this script again.
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Installing required packages...
pip install flask flask-cors pandas selenium openpyxl webdriver-manager
if %errorlevel% neq 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

echo Verifying Flask installation...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Flask installation verification failed. Attempting to install Flask again...
    pip install flask
    if %errorlevel% neq 0 (
        echo Failed to install Flask. Please try installing it manually.
        pause
        exit /b 1
    )
)

echo Downloading ChromeDriver...
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

echo Creating uploads folder...
mkdir uploads

echo Updating app.py with dynamic ChromeDriver path...
powershell -Command "(gc app.py) -replace 'chrome_driver_path = r\".*\"', 'chrome_driver_path = ChromeDriverManager().install()' | Out-File -encoding ASCII app.py"

echo Setup complete!
echo Starting the application...

python app.py

pause