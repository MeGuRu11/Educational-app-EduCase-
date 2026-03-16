@echo off
cd /d %~dp0
if not exist "venv\Scripts\activate.bat" (
    echo [EduCase] Virtual environment not found. Please create one at venv
    pause
    exit /b
)
call venv\Scripts\activate
python run_scenario_builder.py
pause
