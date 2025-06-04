import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="AI Creative Partner",
    page_icon="🎨",
    layout="wide"
)

# Title and description
st.title("🎨 AI Creative Partner")
st.markdown("""
Transform your ideas into stunning 3D models using AI!
""")

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Input form
with st.form("generation_form"):
    prompt = st.text_area(
        "Enter your creative prompt",
        placeholder="Example: A glowing dragon standing on a cliff at sunset",
        height=100
    )
    submitted = st.form_submit_button("Generate")

if submitted and prompt:
    try:
        # Show progress
        with st.spinner("Generating your creation..."):
            # Call the API
            response = requests.post(
                "http://localhost:8888/generate",
                json={"prompt": prompt}
            )
            result = response.json()
            
            # Display results
            st.success("Generation complete!")
            
            # Show enhanced prompt
            st.subheader("Enhanced Prompt")
            st.write(result["enhanced_prompt"])
            
            # Show image
            if result.get("image_url"):
                st.subheader("Generated Image")
                st.image(result["image_url"])
            
            # Show 3D model
            if result.get("model_url"):
                st.subheader("3D Model")
                st.markdown(f"[View 3D Model]({result['model_url']})")
            
            # Add to history
            st.session_state.history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "prompt": prompt,
                "enhanced_prompt": result["enhanced_prompt"],
                "image_url": result.get("image_url"),
                "model_url": result.get("model_url")
            })
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Show history
if st.session_state.history:
    st.sidebar.title("Generation History")
    for item in reversed(st.session_state.history):
        with st.sidebar.expander(f"{item['timestamp']} - {item['prompt'][:30]}..."):
            st.write("Original prompt:", item["prompt"])
            st.write("Enhanced prompt:", item["enhanced_prompt"])
            if item.get("image_url"):
                st.image(item["image_url"], width=200)
            if item.get("model_url"):
                st.markdown(f"[View 3D Model]({item['model_url']})")