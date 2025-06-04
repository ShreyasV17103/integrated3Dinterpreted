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

REM Install Flask and its dependencies first
pip install Flask==2.3.3 Flask-Cors==3.0.10 Flask-RESTful==0.3.10 Flask-SocketIO==5.5.1 Werkzeug==3.1.3 flask-apispec==0.11.4

REM Install gevent
pip install --only-binary :all: gevent==22.10.2

REM Install openfabric-pysdk
pip install openfabric-pysdk==0.2.9

REM Install other requirements
pip install -r requirements.txt

REM Start the FastAPI server
start cmd /k "cd app && uvicorn main:app --host 0.0.0.0 --port 8888"

REM Start the Streamlit UI
start cmd /k "cd app && streamlit run ui.py"

echo Application started!
echo FastAPI server: http://localhost:8888
echo Streamlit UI: http://localhost:8501 