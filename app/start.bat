@echo off
echo Starting AI Creative Partner...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    py -3.11 -m venv venv
    call venv\Scripts\activate.bat
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Start the FastAPI server
start cmd /k "cd app && uvicorn main:app --host 0.0.0.0 --port 8888"

REM Start the Streamlit UI
start cmd /k "cd app && streamlit run ui.py"

echo Application started!
echo FastAPI server: http://localhost:8888
echo Streamlit UI: http://localhost:8501 