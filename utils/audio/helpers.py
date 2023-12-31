from config import AUDIO_SETTINGS
import random

def contains_quiet_please_phrase(input_string):
    """
    Checks if the input string contains any of the phrases that signal a request for quiet.

    Args:
        input_string (str): The string to be checked against quiet please phrases.

    Returns:
        bool: True if any quiet please phrase is found in the input string, False otherwise.
    """
    return any(phrase in input_string for phrase in AUDIO_SETTINGS['QUIET_PLEASE_PHRASES'])

def contains_wake_phrase(input_string):
    """
    Checks if the input string contains any of the wake phrases.

    Args:
        input_string (str): The string to be checked against wake phrases.

    Returns:
        bool: True if any wake phrase is found in the input string, False otherwise.
    """
    return any(phrase in input_string for phrase in AUDIO_SETTINGS['WAKE_PHRASES'])

def get_tool_not_found_phrase():
    """
    Gets a random phrase to use when a tool is not found.

    Returns:
        str: A random phrase to use when a tool is not found.
    """
    return random.choice(AUDIO_SETTINGS['TOOL_NOT_FOUND_PHRASES'])