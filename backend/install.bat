@echo off
REM Installation script for Food Store Backend

echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ✅ Installation complete!
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat (on Windows)
echo   source venv/bin/activate (on Linux/macOS)
echo.
echo To verify installation, run:
echo   python -c "import fastapi; import sqlmodel; print('OK')"
echo.
