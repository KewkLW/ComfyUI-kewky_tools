import folder_paths
from server import PromptServer
import nodes

class CustomNodeWithEmojiMenuItem:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image": ("IMAGE",)}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_image"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def process_image(self, image):
        # Your image processing logic here
        return (image,)

    @classmethod
    def add_custom_menu_item(cls):
        try:
            from comfy.graph import NodeIdNode
        except ImportError as e:
            print(f"ImportError: {e}")
            return

        def do_nothing(node_id):
            # This function does nothing
            pass

        # Check if the PromptServer has the method add_context_menu_option
        if hasattr(PromptServer.instance, 'add_context_menu_option'):
            PromptServer.instance.add_context_menu_option('🧔🏻‍♂️🇰 🇪 🇼 🇰', do_nothing)
            PromptServer.instance.add_context_menu_option('Hello World!', do_nothing)
        else:
            print("PromptServer does not have the method add_context_menu_option")

# Register the custom menu items
CustomNodeWithEmojiMenuItem.add_custom_menu_item()

# Register the node
NODE_CLASS_MAPPINGS = {
    "CustomNodeWithEmojiMenuItem": CustomNodeWithEmojiMenuItem
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomNodeWithEmojiMenuItem": "Custom Node With Emoji Menu Item"
}
