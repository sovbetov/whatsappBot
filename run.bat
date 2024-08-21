@echo off
cd /d "%~dp0venv\Scripts"
call activate
cd /d "%~dp0"
start cmd /k "python app.py"
start "" "index.html"
