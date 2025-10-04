@echo off
echo start...
echo to stop press Ctrl+C
echo.

cd /d "%~dp0"
call venv\Scripts\activate
python direct_email_checker.py

pause
