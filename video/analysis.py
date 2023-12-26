from config import VISION_ANALYSIS_SETTINGS
from utils.os.helpers import OSHelper
import importlib

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
        return self.adapter.analyze_image(image_path, query)
        

vision_analyzer = VisionAnalysisClient()

def get_vision_analyzer():
    """
    Returns the instance of AudioOutput for use.

    Returns:
        VisionAnalysisClient: The instance of the VisionAnalysisClient class.
    """
    return vision_analyzer