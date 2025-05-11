import asyncio
from aiohttp import web
import os
import subprocess
import sys
import inspect
import logging

# Specific logger for this feature
feature_logger = logging.getLogger(__name__) # This will use 'your_custom_node_package_name.open_py_feature'
if not feature_logger.handlers: # Avoid adding multiple handlers if reloaded
    handler = logging.StreamHandler() # Or your preferred handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    feature_logger.addHandler(handler)
    feature_logger.setLevel(logging.INFO) # Set your desired log level

# Global references to be set by the init function
PROMPT_SERVER_INSTANCE = None
NODES_MODULE = None

def get_node_filepath(node_type_name_str):
    if not NODES_MODULE or not hasattr(NODES_MODULE, 'NODE_CLASS_MAPPINGS'):
        feature_logger.error("NODES_MODULE.NODE_CLASS_MAPPINGS is not available. Cannot retrieve node file path.")
        return None

    if node_type_name_str in NODES_MODULE.NODE_CLASS_MAPPINGS:
        node_class_obj = NODES_MODULE.NODE_CLASS_MAPPINGS[node_type_name_str]
        try:
            filepath = inspect.getfile(node_class_obj)
            if filepath and os.path.basename(filepath) == "__init__.py":
                module_dir = os.path.dirname(filepath)
                potential_file = os.path.join(module_dir, node_class_obj.__name__ + ".py")
                if os.path.exists(potential_file):
                    feature_logger.info(f"Resolved {node_class_obj.__name__} from __init__.py to {potential_file}")
                    return potential_file
            return filepath
        except TypeError:
            feature_logger.error(f"Cannot get file for node type '{node_type_name_str}': Not a user-defined class, module, or function.")
            return None
        except Exception as e:
            feature_logger.error(f"Unexpected error in inspect.getfile for '{node_type_name_str}': {e}")
            return None
    else:
        feature_logger.warning(f"Node type '{node_type_name_str}' not found in NODE_CLASS_MAPPINGS.")
        return None

def open_file_os_agnostic(filepath):
    try:
        feature_logger.info(f"Attempting to open file: {filepath} using system default.")
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            subprocess.run(['open', filepath], check=True)
        else:
            subprocess.run(['xdg-open', filepath], check=True)
        feature_logger.info(f"Successfully initiated opening of file: {filepath}")
    except FileNotFoundError:
        feature_logger.error(f"File not found: {filepath}")
        raise
    except subprocess.CalledProcessError as e:
        feature_logger.error(f"Command failed for opening file '{filepath}': {e}")
        raise
    except Exception as e:
        feature_logger.error(f"An unexpected error occurred while trying to open '{filepath}': {e}")
        raise

async def open_node_source_route_handler(request: web.Request):
    try:
        if not request.can_read_body:
            feature_logger.warning("API call to /api/open_node_source: Request body is missing or unreadable.")
            return web.json_response({"error": "Request body is missing or unreadable"}, status=400)
        
        try:
            data = await request.json()
        except ValueError:
            feature_logger.warning("API call to /api/open_node_source: Invalid JSON in request body.")
            return web.json_response({"error": "Invalid JSON in request body"}, status=400)
            
        node_type_name = data.get('node_type')

        if not node_type_name:
            feature_logger.warning("API call to /api/open_node_source missing 'node_type'.")
            return web.json_response({"error": "Missing 'node_type' in request body"}, status=400)

        feature_logger.info(f"Received request to open source for node type: {node_type_name}")
        
        if not NODES_MODULE:
             feature_logger.error("Cannot process /api/open_node_source: 'nodes' module reference unavailable.")
             return web.json_response({"error": "Server configuration error: Node registry not loaded correctly for feature."}, status=500)

        filepath = get_node_filepath(node_type_name)

        if filepath:
            feature_logger.info(f"Found source file for '{node_type_name}' at: {filepath}")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, open_file_os_agnostic, filepath)
                return web.json_response({"message": f"Request to open '{os.path.basename(filepath)}' sent successfully."})
            except Exception as e:
                feature_logger.error(f"Failed to open file '{filepath}' for node '{node_type_name}': {e}")
                return web.json_response({"error": f"Could not open file: {str(e)}"}, status=500)
        else:
            feature_logger.warning(f"Could not find source file for node type: {node_type_name}")
            return web.json_response({"error": f"Source file not found for node type: {node_type_name}"}, status=404)
    except Exception as e:
        feature_logger.exception(f"Critical error in /api/open_node_source route handler: {e}")
        return web.json_response({"error": f"An internal server error occurred: {str(e)}"}, status=500)

def init_open_py_feature(prompt_server_instance, nodes_module_ref):
    global PROMPT_SERVER_INSTANCE, NODES_MODULE
    PROMPT_SERVER_INSTANCE = prompt_server_instance
    NODES_MODULE = nodes_module_ref

    if PROMPT_SERVER_INSTANCE and hasattr(PROMPT_SERVER_INSTANCE, 'app') and NODES_MODULE:
        PROMPT_SERVER_INSTANCE.app.router.add_post('/api/open_node_source', open_node_source_route_handler)
        feature_logger.info("Successfully registered POST '/api/open_node_source' API route for 'Open Py File' feature.")
    else:
        if not PROMPT_SERVER_INSTANCE or not hasattr(PROMPT_SERVER_INSTANCE, 'app'):
            feature_logger.error("PromptServer instance or app not available. API route for 'Open Py File' will not be available.")
        if not NODES_MODULE:
            feature_logger.error("Nodes module reference not available. File path resolution will fail for 'Open Py File' feature.")