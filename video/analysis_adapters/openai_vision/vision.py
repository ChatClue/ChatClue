from utils.os.helpers import OSHelper
from integrations.openai.openai import OpenAIClient
from integrations.openai.openai_conversation_builder import OpenAIConversationBuilder

class OpenAIVisionClient:
    """
    A client class for handling vision analysis using OpenAI's services. This is an adapter for the video.analysis.VisionAnalysisClient class.

    This class provides functionality to analyze images using OpenAI's API. It converts the image into a format
    suitable for analysis, builds a conversation-like structure for the query, and then sends it to OpenAI's
    API for processing. The analysis results are returned as a text response.

    Attributes:
        openai_client (OpenAIClient): An instance of the OpenAIClient class for interacting with OpenAI's API.
        conversation_builder (OpenAIConversationBuilder): An instance of the OpenAIConversationBuilder class to 
                                                          build a conversation-like structure for the image analysis query.
    """

    def __init__(self):
        """
        Initializes the OpenAIVisionClient class.

        Sets up the OpenAIClient and OpenAIConversationBuilder required for analyzing images using OpenAI's API.
        """
        self.openai_client = OpenAIClient()  # Initialize the OpenAI API client
        self.conversation_builder = OpenAIConversationBuilder()  # Initialize the conversation builder

    def analyze_image(self, image_path: str, query: str) -> str:
        """
        Analyzes an image using OpenAI's API.

        This method takes the path to an image and a query string, converts the image to base64 for processing,
        constructs a conversation-like array using the query, and sends it to OpenAI's API. The response from
        OpenAI's API is then returned.

        Args:
            image_path (str): The file path of the image to be analyzed.
            query (str): A query string describing what analysis to perform on the image.

        Returns:
            str: The analysis result returned by OpenAI's API.
        """
        data = OSHelper.convert_image_to_base64(image_path)  # Convert image to base64
        conversation = self.conversation_builder.create_recent_conversation_messages_array(query, True, 0, data)  # Build the conversation array
        response = self.openai_client.create_completion(conversation, False, None, None, False)  # Get the analysis from OpenAI
        return response.choices[0].message.content  # Return the content of the response
