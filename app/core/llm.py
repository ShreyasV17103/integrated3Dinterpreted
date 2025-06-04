import os
from typing import Dict, List, Optional
from openfabric_pysdk.stub import Stub
from openfabric_pysdk.context import Config

class OpenfabricClient:
    def __init__(self):
        """Initialize the Openfabric client."""
        self.config = Config(
            app_id=os.getenv("OPENFABRIC_TEXT_TO_IMAGE_APP_ID"),
            api_key=os.getenv("OPENFABRIC_API_KEY")
        )
        self.stub = Stub(self.config)
        
    def generate_image(self, prompt: str) -> str:
        """Generate an image from a text prompt.
        
        Args:
            prompt (str): Text prompt for image generation
            
        Returns:
            str: URL of the generated image
        """
        response = self.stub.generate_image(prompt=prompt)
        return response.image_url
    
    def generate_3d_model(self, image_url: str) -> str:
        """Generate a 3D model from an image.
        
        Args:
            image_url (str): URL of the input image
            
        Returns:
            str: URL of the generated 3D model
        """
        config = Config(
            app_id=os.getenv("OPENFABRIC_IMAGE_TO_3D_APP_ID"),
            api_key=os.getenv("OPENFABRIC_API_KEY")
        )
        stub = Stub(config)
        response = stub.generate_3d_model(image_url=image_url)
        return response.model_url

# Create a singleton instance
openfabric_client = OpenfabricClient()