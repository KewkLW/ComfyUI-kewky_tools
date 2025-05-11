import logging

# Configure a base logger for your package if you don't have one
# This is optional, but good practice.
package_logger = logging.getLogger(__name__) # This will be 'your_custom_node_package_name'
if not package_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    package_logger.addHandler(handler)
    package_logger.setLevel(logging.INFO)


# Attempt to import ComfyUI server and nodes modules - needed for the open_py_feature
try:
    from server import PromptServer
except ImportError:
    try:
        import main
        if hasattr(main, 'server_instance'):
            PromptServer = main.server_instance.__class__
            PromptServer.instance = main.server_instance
            package_logger.info("Successfully imported PromptServer instance via main.server_instance.")
        else:
            if 'PromptServer' in globals() and hasattr(globals()['PromptServer'], 'instance'):
                 PromptServer = globals()['PromptServer']
                 package_logger.info("Used globally available PromptServer instance.")
            else:
                raise ImportError("PromptServer instance not found in main or global scope.")
    except Exception as e:
        package_logger.error(f"Failed to import PromptServer: {e}. The 'Open Py File' API route might not be available.")
        PromptServer = None

try:
    import nodes
except ImportError:
    package_logger.error("Failed to import 'nodes' module from ComfyUI. 'Open Py File' feature might not work correctly.")
    nodes = None

# --- Your existing imports for other nodes ---
from .text_append_node import NODE_CLASS_MAPPINGS as TEXT_APPEND_NODE_CLASS_MAPPINGS
from .text_append_node import NODE_DISPLAY_NAME_MAPPINGS as TEXT_APPEND_NODE_DISPLAY_NAME_MAPPINGS
from .vramdebugplus import NODE_CLASS_MAPPINGS as VRAM_DEBUG_PLUS_NODE_CLASS_MAPPINGS
from .vramdebugplus import NODE_DISPLAY_NAME_MAPPINGS as VRAM_DEBUG_PLUS_NODE_DISPLAY_NAME_MAPPINGS
from .tensordebugplus import NODE_CLASS_MAPPINGS as TENSOR_DEBUG_PLUS_NODE_CLASS_MAPPINGS
from .tensordebugplus import NODE_DISPLAY_NAME_MAPPINGS as TENSOR_DEBUG_PLUS_NODE_DISPLAY_NAME_MAPPINGS
from .animation_schedule_output import NODE_CLASS_MAPPINGS as ANIMATION_SCHEDULE_OUTPUT_NODE_CLASS_MAPPINGS
from .animation_schedule_output import NODE_DISPLAY_NAME_MAPPINGS as ANIMATION_SCHEDULE_OUTPUT_NODE_DISPLAY_NAME_MAPPINGS
from .clipinterrogator import NODE_CLASS_MAPPINGS as CLIP_INTERROGATOR_NODE_CLASS_MAPPINGS
from .clipinterrogator import NODE_DISPLAY_NAME_MAPPINGS as CLIP_INTERROGATOR_NODE_DISPLAY_NAME_MAPPINGS
from .image_batcher import NODE_CLASS_MAPPINGS as IMAGE_BATCHER_NODE_CLASS_MAPPINGS
from .image_batcher import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_BATCHER_NODE_DISPLAY_NAME_MAPPINGS
from .text_search_node import NODE_CLASS_MAPPINGS as TEXT_SEARCH_NODE_CLASS_MAPPINGS
from .text_search_node import NODE_DISPLAY_NAME_MAPPINGS as TEXT_SEARCH_NODE_DISPLAY_NAME_MAPPINGS
from .LoadImagePlus import NODE_CLASS_MAPPINGS as LOAD_IMAGE_PLUS_NODE_CLASS_MAPPINGS
from .LoadImagePlus import NODE_DISPLAY_NAME_MAPPINGS as LOAD_IMAGE_PLUS_NODE_DISPLAY_NAME_MAPPINGS
from .LoadVideoPlus import NODE_CLASS_MAPPINGS as LOAD_VIDEO_PLUS_NODE_CLASS_MAPPINGS
from .LoadVideoPlus import NODE_DISPLAY_NAME_MAPPINGS as LOAD_VIDEO_PLUS_NODE_DISPLAY_NAME_MAPPINGS
# --- End of your existing imports ---

# Import and initialize the "Open Py File" feature
from . import open_py_feature # Use 'from .' to ensure it's relative to the current package
if PromptServer and hasattr(PromptServer, 'instance') and nodes:
    open_py_feature.init_open_py_feature(PromptServer.instance, nodes)
else:
    package_logger.warning("'Open Py File' feature could not be initialized due to missing PromptServer or nodes module.")


# --- Your existing NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS ---
_NODE_CLASS_MAPPINGS = {
    **TEXT_APPEND_NODE_CLASS_MAPPINGS,
    **VRAM_DEBUG_PLUS_NODE_CLASS_MAPPINGS,
    **TENSOR_DEBUG_PLUS_NODE_CLASS_MAPPINGS,
    **ANIMATION_SCHEDULE_OUTPUT_NODE_CLASS_MAPPINGS,
    **CLIP_INTERROGATOR_NODE_CLASS_MAPPINGS,
    **IMAGE_BATCHER_NODE_CLASS_MAPPINGS,
    **TEXT_SEARCH_NODE_CLASS_MAPPINGS,
    **LOAD_IMAGE_PLUS_NODE_CLASS_MAPPINGS,
    **LOAD_VIDEO_PLUS_NODE_CLASS_MAPPINGS,
}

_NODE_DISPLAY_NAME_MAPPINGS = {
    **TEXT_APPEND_NODE_DISPLAY_NAME_MAPPINGS,
    **VRAM_DEBUG_PLUS_NODE_DISPLAY_NAME_MAPPINGS,
    **TENSOR_DEBUG_PLUS_NODE_DISPLAY_NAME_MAPPINGS,
    **ANIMATION_SCHEDULE_OUTPUT_NODE_DISPLAY_NAME_MAPPINGS,
    **CLIP_INTERROGATOR_NODE_DISPLAY_NAME_MAPPINGS,
    **IMAGE_BATCHER_NODE_DISPLAY_NAME_MAPPINGS,
    **TEXT_SEARCH_NODE_DISPLAY_NAME_MAPPINGS,
    **LOAD_IMAGE_PLUS_NODE_DISPLAY_NAME_MAPPINGS,
    **LOAD_VIDEO_PLUS_NODE_DISPLAY_NAME_MAPPINGS,
}
# --- End of your existing mappings ---

# Define WEB_DIRECTORY for the JavaScript file(s)
# Ensure your open_py.js is in a 'js' subdirectory within this custom node package.
WEB_DIRECTORY = "./js"

# Final export (ensure WEB_DIRECTORY is included if ComfyUI checks __all__ for it,
# though it often discovers it as a top-level variable regardless)
NODE_CLASS_MAPPINGS = _NODE_CLASS_MAPPINGS
NODE_DISPLAY_NAME_MAPPINGS = _NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

package_logger.info("Custom node package initialized, including 'Open Py File' feature if server and nodes modules were available.")