import inspect
import json
import sys

openai_functions = []

def openai_function(func):
    """
    Decorator to mark a function as an OpenAI tool and extract its metadata.
    """
    # Extract information from the docstring
    doc = inspect.getdoc(func)
    try:
        metadata = json.loads(doc)
    except json.JSONDecodeError:
        metadata = {"description": doc, "parameters": {}}

    # Get the full module path
    module_name = func.__module__
    full_name = f"{module_name}.{func.__name__}"

    # Register the function with its full path
    openai_functions.append({
        "type": "function",
        "function": {
            "name": func.__name__,
            "full_name": full_name,
            **metadata
        }
    })

    return func
