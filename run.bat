@echo off
echo ============================
echo Setting up Project
echo ============================

REM Check if venv exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Starting Streamlit app...
streamlit run app.py

pause
