import logging
from config import VIDEO_SETTINGS
from decorators.openai_decorators import openai_function
from datetime import datetime
from database.system_state import SystemStateManager 
from video.analysis import get_vision_analyzer
from utils.os.helpers import OSHelper


if VIDEO_SETTINGS.get("CAPTURE_VIDEO", True):
    @openai_function
    def analyze_image_based_on_users_request(users_request):
        """
        {
            "description": "If a user asks the robot 'What is this?' or 'What do you see?' or 'Can you tell the difference', or any other user type question that may imply a visual requirement, this function will use the system's video output to analyze the user's request and return a description",
            "is_conversational": true,
            "parameters": {
                "type": "object",
                "properties": {
                    "users_request": {
                        "type": "string",
                        "description": "What is the user asking?"
                    }
                },
                "required": ["users_request"]
            }
        }
        """
        state_manager = SystemStateManager()
        vision_client = get_vision_analyzer()

        state = state_manager.get_or_create_state()

        if state.last_wake_time is None:
            return "Something went wrong while processing the state request. Please try again."
        
        # Convert last_wake_time to datetime
        last_wake_datetime = datetime.fromtimestamp(state.last_wake_time)

        # Find the closest image file
        closest_image_path = OSHelper.find_closest_image("tmp/video/", last_wake_datetime.timestamp())
        logging.info(f"Closest image path: {closest_image_path}")
        if closest_image_path:
            # Analyze the image
            description = vision_client.analyze_image(closest_image_path, users_request)
            logging.info(f"Image analysis result: {description}")
            return description    
        else:
            return "Something went wrong processing the request. Please try again."
