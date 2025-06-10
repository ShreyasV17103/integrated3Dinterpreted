import os
import requests

class OpenfabricClient:
    def __init__(self):
        """Initialize the Openfabric client."""
        self.text_to_image_app_id = os.getenv("TEXT_TO_IMAGE_APP_ID")
        self.image_to_3d_app_id = os.getenv("IMAGE_TO_3D_APP_ID")
        # self.api_key = os.getenv("OPENFABRIC_API_KEY")
        # self.base_url = "https://api.openfabric.network/v1/apps"

    def generate_image(self, prompt: str) -> str:
        """Generate an image from a text prompt.
        
        Args:
            prompt (str): Text prompt for image generation
            
        Returns:
            str: URL of the generated image
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"prompt": prompt}
        response = requests.post(
            f"{self.base_url}/{self.text_to_image_app_id}/generate",
            headers=headers,
            json=data
        )
        return response.json().get("image_url")
    
    def generate_3d_model(self, image_url: str) -> str:
        """Generate a 3D model from an image.
        
        Args:
            image_url (str): URL of the input image
            
        Returns:
            str: URL of the generated 3D model
        """
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"image_url": image_url}
        response = requests.post(
            f"{self.base_url}/{self.image_to_3d_app_id}/generate",
            headers=headers,
            json=data
        )
        return response.json().get("model_url")

# Create a singleton instance
openfabric_client = OpenfabricClient()