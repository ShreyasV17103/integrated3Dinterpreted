import os
import json
from typing import Dict, List, Optional
import requests
from pydantic import BaseModel

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client.
        
        Args:
            base_url (str): Base URL for the Ollama API. Defaults to localhost.
        """
        self.base_url = base_url
        self.model = os.getenv("OLLAMA_MODEL", "deepseek-coder")
        
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make a request to the Ollama API.
        
        Args:
            endpoint (str): API endpoint
            data (Dict): Request data
            
        Returns:
            Dict: API response
        """
        response = requests.post(f"{self.base_url}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt (str): User prompt
            system (Optional[str]): System prompt to guide the model
            
        Returns:
            str: Generated response
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            data["system"] = system
            
        response = self._make_request("api/generate", data)
        return response["response"]
    
    def enhance_prompt(self, original_prompt: str) -> str:
        """Enhance a creative prompt using the LLM.
        
        Args:
            original_prompt (str): Original user prompt
            
        Returns:
            str: Enhanced prompt
        """
        system_prompt = """You are an expert creative prompt engineer. Your task is to enhance the given prompt 
        to create more detailed and vivid descriptions that will help generate better 3D models. 
        Focus on adding specific details about:
        - Lighting and atmosphere
        - Materials and textures
        - Perspective and composition
        - Fine details and features
        Keep the core idea intact while making it more descriptive."""
        
        prompt = f"""Please enhance this creative prompt for 3D model generation:
        
        Original prompt: {original_prompt}
        
        Provide only the enhanced prompt without any explanations."""
        
        return self.generate(prompt, system_prompt)
    
    def analyze_prompt(self, prompt: str) -> Dict:
        """Analyze a prompt to extract key elements and requirements.
        
        Args:
            prompt (str): User prompt
            
        Returns:
            Dict: Analysis containing key elements and requirements
        """
        system_prompt = """You are an expert at analyzing creative prompts. Extract key elements and requirements 
        that would be important for 3D model generation. Focus on:
        - Main subject and its characteristics
        - Environment and setting
        - Lighting and atmosphere
        - Technical requirements
        Return the analysis as a JSON object."""
        
        prompt = f"""Analyze this creative prompt:
        
        {prompt}
        
        Return the analysis as a JSON object with the following structure:
        {{
            "main_subject": "description",
            "environment": "description",
            "lighting": "description",
            "technical_requirements": ["requirement1", "requirement2"]
        }}"""
        
        response = self.generate(prompt, system_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "main_subject": "Unknown",
                "environment": "Unknown",
                "lighting": "Unknown",
                "technical_requirements": []
            }

# Create a singleton instance
llm_client = OllamaClient()