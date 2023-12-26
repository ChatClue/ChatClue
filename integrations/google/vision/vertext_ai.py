import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from utils.os.helpers import OSHelper
from config import GOOGLE_VISION_SETTINGS

class VertexAIClient:
    def __init__(self):
        """
        Initializes VertexAIImageAnalyzer with Google Cloud credentials.
        Sets up the Vertex AI environment and loads the Gemini Pro Vision model.
        """
        if 'api_key_path' in GOOGLE_VISION_SETTINGS:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_VISION_SETTINGS['api_key_path']
        
        # Initialize Vertex AI with the project ID and location from the config
        vertexai.init(project=GOOGLE_VISION_SETTINGS['project_id'], location=GOOGLE_VISION_SETTINGS['location'])
        
        # Load the Gemini Pro Vision model
        self.model = GenerativeModel(GOOGLE_VISION_SETTINGS['model'])

    def analyze_image(self, image_path: str, query: str) -> str:
        """
        Analyzes an image using the Gemini Pro Vision model and returns a description based on the provided query.

        Args:
            image_path (str): The file path to the image to be analyzed.
            query (str): The query string to provide context or specify the type of information needed about the image.

        Returns:
            str: The API's response text describing the image based on the query.
        """
        data = OSHelper.convert_image_to_base64(image_path)
        
        # Query the model
        response = self.model.generate_content(
            [
                Part.from_data(data, "image/jpeg"),  # Add the image
                query,                               # Add the query
            ]
        )
        return response.text