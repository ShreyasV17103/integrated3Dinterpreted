import streamlit as st
import requests
import json
from pathlib import Path
import base64
from PIL import Image
import io

st.set_page_config(page_title="AI Creative Partner", page_icon="🎨", layout="wide")

st.title("🎨 AI Creative Partner")
st.markdown("Transform your ideas into stunning 3D models!")

# Sidebar for memory
st.sidebar.title("Memory")
st.sidebar.markdown("View your past generations")

# Main content
prompt = st.text_area("Enter your creative prompt:", height=100)
if st.button("Generate"):
    if prompt:
        with st.spinner("Generating your creation..."):
            try:
                # Call the API
                response = requests.post(
                    "http://localhost:8888/execution",
                    json={"prompt": prompt}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display the image
                    if result.get("image_path"):
                        st.image(result["image_path"], caption="Generated Image", use_column_width=True)
                    
                    # Display the 3D model
                    if result.get("model_path"):
                        st.markdown("### 3D Model")
                        st.markdown(f"Download your 3D model: [GLB File]({result['model_path']})")
                    
                    # Display memory info
                    if result.get("memory"):
                        st.sidebar.markdown("### Latest Generation")
                        st.sidebar.json(result["memory"])
                
                else:
                    st.error("Failed to generate. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a prompt first!")

# Display memory in sidebar
try:
    response = requests.get("http://localhost:8888/memory")
    if response.status_code == 200:
        memory = response.json()
        if memory:
            st.sidebar.markdown("### Past Generations")
            for entry in memory[:5]:  # Show last 5 generations
                st.sidebar.markdown(f"**Prompt:** {entry['prompt']}")
                st.sidebar.markdown(f"**Date:** {entry['timestamp']}")
                st.sidebar.markdown("---")
except:
    pass