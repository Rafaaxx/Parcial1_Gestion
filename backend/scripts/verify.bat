@echo off
REM Backend verification script for Food Store

echo ========================================
echo Food Store Backend Verification
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not installed
    exit /b 1
)
echo OK
echo.

REM Check FastAPI import
echo [2/5] Checking FastAPI import...
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
if %errorlevel% neq 0 (
    echo ERROR: FastAPI not installed. Run: pip install -r requirements.txt
    exit /b 1
)
echo OK
echo.

REM Check SQLModel import
echo [3/5] Checking SQLModel import...
python -c "import sqlmodel; print('SQLModel OK')"
if %errorlevel% neq 0 (
    echo ERROR: SQLModel not installed
    exit /b 1
)
echo OK
echo.

REM Check .env file
echo [4/5] Checking .env file...
if not exist ".env" (
    echo ERROR: .env file not found. Copy from .env.example: copy .env.example .env
    exit /b 1
)
echo OK
echo.

REM Check app structure
echo [5/5] Checking project structure...
if not exist "app" (
    echo ERROR: app/ directory not found
    exit /b 1
)
if not exist "app\main.py" (
    echo ERROR: app/main.py not found
    exit /b 1
)
if not exist "app\config.py" (
    echo ERROR: app/config.py not found
    exit /b 1
)
if not exist "app\database.py" (
    echo ERROR: app/database.py not found
    exit /b 1
)
echo OK
echo.

echo ========================================
echo All checks passed!
echo ========================================
echo.
echo Next steps:
echo 1. Ensure PostgreSQL is running on localhost:5432
echo 2. Run migrations: alembic upgrade head
echo 3. Start dev server: uvicorn app.main:app --reload
echo 4. Visit http://localhost:8000/docs for API docs
echo.
