# __init__.py
from .tensordebugplus import TensorDebugPlus
from .animation_schedule_output import FormattedPromptNode

NODE_CLASS_MAPPINGS = {
    "TensorDebugPlus": TensorDebugPlus,
    "FormattedTextOutput": FormattedPromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TensorDebugPlus": "Tensor Debug++",
    "FormattedTextOutput": "Formatted Text Output",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']