#!/bin/bash

py -3.11 -m venv venv
venv\Scripts\activate

pip install -r requirements.txt


cd app
uvicorn main:app --host 0.0.0.0 --port 8888
streamlit run ui.py