import inspect
import os
from pathlib import Path
import importlib.util
import sys
import os

def get_callable_path(callable_obj: callable) -> Path:
    file_path = inspect.getfile(callable_obj)
    absolute_path = os.path.abspath(file_path)
    return Path(absolute_path)

def get_callable_from_path(module_path, function_name):
    """
    Dynamically imports a module from a file path and retrieves a callable function.

    Args:
        module_path (str or pathlib.Path): The path to the Python file.
        function_name (str): The name of the function within the module.

    Returns:
        callable: The function object.
    """
    module_path = os.path.abspath(module_path)
    module_name = os.path.splitext(os.path.basename(module_path))[0]

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"Could not find a spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    
    # Register the module with sys.modules (optional but good practice)
    sys.modules[module_name] = module
    
    # Execute the module to load its contents (e.g., function definitions)
    spec.loader.exec_module(module)

    # Use getattr to retrieve the function object
    try:
        function_obj = getattr(module, function_name)
    except AttributeError:
        raise AttributeError(f"Function '{function_name}' not found in module '{module_name}'")

    return function_obj
