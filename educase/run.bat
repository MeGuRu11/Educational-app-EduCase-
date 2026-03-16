@echo off
cd /d %~dp0

:: 1. Проверка виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo [EduCase] Virtual environment not found. Please create one at venv
    pause
    exit /b
)
call venv\Scripts\activate

:: 2. Установка зависимостей (тихая установка, обновит если нужно)
echo [EduCase] Checking/installing dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [EduCase] Failed to install requirements.
    pause
    exit /b
)

:: 3. Проверка пользователей и запуск seed.py если БД пуста
echo [EduCase] Checking database users...
python -m services.seed

:: 4. Запуск приложения
echo [EduCase] Starting application...
python main.py
pause
