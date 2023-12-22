import logging
import json
from decorators.openai_decorators import openai_functions

class ToolProcessor:
    """
    Processes tool requests from OpenAI responses and executes corresponding functions.

    This class is responsible for identifying the tool function to be executed based on the OpenAI response,
    parsing any arguments, and invoking the function. It handles the successful or unsuccessful execution of these tools.
    """

    def __init__(self):
        """
        Initializes the ToolProcessor.
        """
        pass  # No initialization required at the moment

    def process_tool_request(self, tool_response):
        """
        Processes a tool request based on the response from OpenAI.

        Args:
            tool_response: The response object from OpenAI indicating a tool function call.

        Returns:
            dict: A dictionary containing the status of the tool processing, the result, and other relevant information.
        """
        # Initialize default response structure
        response = {
            "success": False,
            "tool_call_id": None,
            "is_conversational": False,
            "function_result": None,
            "tool_name": None
        }
        tool_name = tool_response.function.name
        logging.info(f"Processing tool request for {tool_name}")

        # Retrieve the function based on the tool name
        tool_function = self.get_function_by_name(tool_name)
        if not tool_function:
            logging.error(f"No tool found for name: {tool_name}")
            return response

        # Check if the tool requires additional conversation
        response["is_conversational"] = self.get_is_conversational_by_name(tool_name)

        # Parse arguments for the tool function
        try:
            arguments = json.loads(tool_response.function.arguments)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse tool arguments: {e}")
            return response

        # Attempt to execute the tool function
        try:
            response["function_result"] = tool_function(**arguments)
            response["success"] = True
        except TypeError as e:
            logging.error(f"Exception running function {tool_name}: {e}")

        # Update response with tool call details
        response["tool_call_id"] = tool_response.id
        response["tool_name"] = tool_name

        return response

    def get_function_by_name(self, tool_name):
        """
        Retrieves a function by its name from the registered OpenAI functions.

        Args:
            tool_name (str): The name of the tool function.

        Returns:
            function: The Python function corresponding to the tool name, or None if not found.
        """
        for tool in openai_functions:
            if tool['function']['name'] == tool_name:
                full_name = tool['function']['full_name']
                return self.import_function(full_name)
        return None
    
    def get_is_conversational_by_name(self, tool_name):
        """
        Checks if a tool function is conversational based on its name.

        Args:
            tool_name (str): The name of the tool function.

        Returns:
            bool: True if the tool function is conversational, False otherwise.
        """
        for tool in openai_functions:
            if tool['function']['name'] == tool_name:
                return tool['function'].get('is_conversational', False)
        return False

    def import_function(self, full_name):
        """
        Dynamically imports a function from a module based on its full name.

        Args:
            full_name (str): The full name of the function including the module path.

        Returns:
            function: The imported function.
        """
        module_name, func_name = full_name.rsplit('.', 1)
        module = __import__(module_name, fromlist=[func_name])
        return getattr(module, func_name)
