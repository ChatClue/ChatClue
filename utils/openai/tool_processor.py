import logging
import json
from decorators.openai_decorators import openai_functions

class ToolProcessor:
    def __init__(self):
        pass

    def process_tool_request(self, tool_response):
        response = {"success": False, "tool_call_id": None, "is_conversational": False, "function_result": None, "tool_name": None}
        tool_name = tool_response.function.name
        print("D"*200)
        print(tool_name)
        tool_function = self.get_function_by_name(tool_name)

        if not tool_function:
            logging.error(f"No tool found for name: {tool_name}")
            return response 
        
        response["is_conversational"] = self.get_is_conversational_by_name(tool_name)
        
        try:
            arguments = json.loads(tool_response.function.arguments)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse tool arguments: {e}")
            return response
        
        try: 
            response["function_result"] = tool_function(**arguments)
            response["success"] = True
        except TypeError as e:
            logging.error(f"Exception running function {tool_name}: {e}")
        
        response["tool_call_id"] = tool_response.id
        response["tool_name"] = tool_name
        return response

    def get_function_by_name(self, tool_name):
        for tool in openai_functions:
            if tool['function']['name'] == tool_name:
                full_name = tool['function']['full_name']
                return self.import_function(full_name)
        return None
    
    def get_is_conversational_by_name(self, tool_name):
        for tool in openai_functions:
            if tool['function']['name'] == tool_name:
                return tool['function']['is_conversational']
        return False

    def import_function(self, full_name):
        module_name, func_name = full_name.rsplit('.', 1)
        module = __import__(module_name, fromlist=[func_name])
        return getattr(module, func_name)
