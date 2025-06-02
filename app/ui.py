import streamlit as st
import sqlite3
from datetime import datetime
import requests
   
st.title("AI Creative Pipeline")
   
   # Prompt input
prompt = st.text_input("Enter your creative prompt:")
   
if st.button("Generate"):
       # Call the API
       response = requests.post(
           "http://localhost:8888/execution",
           json={"prompt": prompt}
       )
       
       if response.status_code == 200:
           result = response.json()
           st.success(result["message"])
           
           # Display generated image
           st.image(result["image_path"])
           
           # Display 3D model (if supported by browser)
           st.components.v1.iframe(result["model_path"])