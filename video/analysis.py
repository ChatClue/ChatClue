from config import VISION_ANALYSIS_SETTINGS
from utils.os.helpers import OSHelper
import importlib
import logging

class VisionAnalysisClient:
    """
    Manages video frame vision analysis.

    This class takes a video frame and analyzes it using the configured vision analysis service.
    """
    def __init__(self):
        """
        Initializes the AudioOutput class with a dynamically selected TTS adapter, required threads, and pygame mixer settings.
        """
        adapter_path = VISION_ANALYSIS_SETTINGS['adapter']
        module_name, class_name = adapter_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        adapter_class = getattr(module, class_name)
        self.adapter = adapter_class() 

    def analyze_image(self, image_path: str, query: str) -> str:
        """
        Analyzes an image based on the given query using the configured vision analysis adapter.

        This method takes the path to an image file and a query string, and utilizes the selected
        vision analysis adapter to perform the analysis. The analysis could range from object
        detection, scene description to more complex interpretations, depending on the capabilities
        of the chosen adapter and the nature of the query.

        Args:
            image_path (str): The file path of the image to be analyzed. This should be a valid path
                              to an image file accessible by the system.
            query (str): A query string describing the analysis to be performed on the image. The query
                         can vary based on what the adapter is capable of processing.

        Returns:
            str: The analysis result as a string. The format and content of this string depend on the
                 adapter's implementation and the nature of the query.

        Example:
            >>> vision_client = VisionAnalysisClient()
            >>> result = vision_client.analyze_image("/path/to/image.jpg", "Describe this scene.")
            >>> print(result)
        """
        return self.adapter.analyze_image(image_path, query)
        

vision_analyzer = VisionAnalysisClient()

def get_vision_analyzer():
    """
    Returns the instance of AudioOutput for use.

    Returns:
        VisionAnalysisClient: The instance of the VisionAnalysisClient class.
    """
    return vision_analyzer