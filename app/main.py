import logging
import os
from typing import Dict, Optional
import json
from datetime import datetime
from pathlib import Path
import requests
import sqlite3
from dataclasses import dataclass
from typing import List
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openfabric import Stub, AppModel, ConfigClass, InputClass, OutputClass

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from core.stub import Stub
from core.llm import llm_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Creative Partner")

# Initialize Openfabric Stub
stub = Stub([
    os.getenv("OPENFABRIC_TEXT_TO_IMAGE_APP_ID"),
    os.getenv("OPENFABRIC_IMAGE_TO_3D_APP_ID")
])

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

# Memory storage
MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-coder"  # or "llama2" or any other model you have pulled

def check_ollama_availability() -> bool:
    """Check if Ollama server is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def init_memory_db():
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS generations
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                prompt TEXT,
                enhanced_prompt TEXT,
                image_path TEXT,
                model_path TEXT,
                image_data BLOB,
                model_data BLOB)''')
    conn.commit()
    conn.close()

init_memory_db()

def save_to_memory(prompt: str, enhanced_prompt: str, image_path: str, model_path: str, image_data: bytes, model_data: bytes) -> None:
    """Save the generation details to SQLite database."""
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('''INSERT INTO generations (timestamp, prompt, enhanced_prompt, image_path, model_path, image_data, model_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (datetime.now().isoformat(), prompt, enhanced_prompt, image_path, model_path, image_data, model_data))
    conn.commit()
    conn.close()

def load_memory() -> List[dict]:
    """Load all memory entries from SQLite database."""
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('SELECT * FROM generations ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    
    return [{
        'id': row[0],
        'timestamp': row[1],
        'prompt': row[2],
        'enhanced_prompt': row[3],
        'image_path': row[4],
        'model_path': row[5],
        'image_data': base64.b64encode(row[6]).decode() if row[6] else None,
        'model_data': base64.b64encode(row[7]).decode() if row[7] else None
    } for row in rows]

def find_similar_prompt(prompt: str) -> Optional[dict]:
    """Find a similar prompt from memory using simple keyword matching."""
    memory = load_memory()
    prompt_words = set(prompt.lower().split())
    
    best_match = None
    best_score = 0
    
    for entry in memory:
        memory_words = set(entry['prompt'].lower().split())
        common_words = prompt_words.intersection(memory_words)
        score = len(common_words) / max(len(prompt_words), len(memory_words))
        
        if score > best_score and score > 0.3:  # Threshold for similarity
            best_score = score
            best_match = entry
    
    return best_match

def enhance_prompt(prompt: str) -> str:
    """Enhance the prompt using Ollama LLM."""
    if not check_ollama_availability():
        logging.error("Ollama server is not running. Please start it using 'ollama serve'")
        return prompt

    try:
        # Check if we have a similar prompt in memory
        similar = find_similar_prompt(prompt)
        if similar:
            logging.info(f"Found similar prompt in memory: {similar['prompt']}")
            prompt = f"Based on this previous request '{similar['prompt']}', enhance this new request: {prompt}"
        
        # Prepare the system message and prompt
        system_message = """You are an expert at enhancing visual descriptions for AI image generation. 
        Your task is to expand the given prompt with rich details about:
        - Visual elements and composition
        - Lighting and atmosphere
        - Colors and textures
        - Style and mood
        Keep the core idea but make it more vivid and detailed."""
        
        # Call Ollama API
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{system_message}\n\nOriginal prompt: {prompt}\n\nEnhanced prompt:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            enhanced = result.get('response', '').strip()
            
            # If the response is empty or just whitespace, return original prompt
            if not enhanced:
                return prompt
                
            # Clean up the response
            enhanced = enhanced.replace("Enhanced prompt:", "").strip()
            logging.info(f"Enhanced prompt: {enhanced}")
            return enhanced
            
        else:
            logging.error(f"Ollama API error: {response.status_code} - {response.text}")
            return prompt
            
    except Exception as e:
        logging.error(f"Error enhancing prompt with Ollama: {e}")
        return prompt

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf

############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """
    # Retrieve input
    request: InputClass = model.request
    prompt = request.prompt

    # Enhance prompt using local LLM
    enhanced_prompt = enhance_prompt(prompt)
    logging.info(f"Enhanced prompt: {enhanced_prompt}")

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"{configurations}")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else []
    stub = Stub(app_ids)

    try:
        # Step 1: Generate image using Text-to-Image app
        text_to_image_app = "f0997a01-d6d3-a5fe-53d8-561300318557.node3.openfabric.network"
        image_result = stub.call(text_to_image_app, {'prompt': enhanced_prompt}, 'super-user')
        
        if not image_result or 'result' not in image_result:
            raise Exception("Failed to generate image")
        
        # Save the generated image
        image_path = f"memory/output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image_data = image_result.get('result')
        with open(image_path, 'wb') as f:
            f.write(image_data)

        # Step 2: Convert image to 3D using Image-to-3D app
        image_to_3d_app = "69543f29-4d41-4afc-7f29-3d51591f11eb.node3.openfabric.network"
        model_result = stub.call(image_to_3d_app, {'image': image_data}, 'super-user')
        
        if not model_result or 'result' not in model_result:
            raise Exception("Failed to generate 3D model")
        
        # Save the 3D model
        model_path = f"memory/model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.glb"
        model_data = model_result.get('result')
        with open(model_path, 'wb') as f:
            f.write(model_data)

        # Save to memory
        save_to_memory(prompt, enhanced_prompt, image_path, model_path, image_data, model_data)

        # Prepare response
        response: OutputClass = model.response
        response.message = f"Successfully generated 3D model from prompt: {prompt}"
        response.image_path = image_path
        response.model_path = model_path
        
        # Add memory information
        memory = load_memory()
        response.memory = {
            'total_generations': len(memory),
            'latest_generation': memory[0] if memory else None
        }

    except Exception as e:
        logging.error(f"Error during execution: {e}")
        response: OutputClass = model.response
        response.message = f"Error: {str(e)}"
        response.error = True

class GenerationRequest(BaseModel):
    prompt: str
    user_id: str = "super-user"

class GenerationResponse(BaseModel):
    message: str
    enhanced_prompt: Optional[str] = None
    image_url: Optional[str] = None
    model_url: Optional[str] = None

@app.post("/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest):
    try:
        # Get the LLM client
        from core.llm import llm_client
        
        # Enhance the prompt using LLM
        enhanced_prompt = llm_client.enhance_prompt(request.prompt)
        
        # Generate image using Openfabric
        image_result = stub.call(
            os.getenv("OPENFABRIC_TEXT_TO_IMAGE_APP_ID"),
            {"prompt": enhanced_prompt},
            request.user_id
        )
        
        # Convert image to 3D model
        model_result = stub.call(
            os.getenv("OPENFABRIC_IMAGE_TO_3D_APP_ID"),
            {"image": image_result.get("result")},
            request.user_id
        )
        
        return GenerationResponse(
            message="Generation successful",
            enhanced_prompt=enhanced_prompt,
            image_url=image_result.get("url"),
            model_url=model_result.get("url")
        )
        
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)