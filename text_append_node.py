# text_append_node.py

class TextAppendNode:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "current_text": ("STRING", {"multiline": True}),
                "append_text": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "append_text"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def append_text(self, current_text, append_text):
        current_lines = [line.strip() for line in current_text.split('\n') if line.strip()]
        append_lines = [line.strip() for line in append_text.split('\n') if line.strip()]
        
        result = []
        
        # If current_text is empty, start with append_text
        if not current_lines:
            return (append_text,)
        
        # Append new text to each line of the current text
        for current_line in current_lines:
            for append_line in append_lines:
                result.append(f"{current_line} {append_line}")
        
        return ('\n'.join(result),)

NODE_CLASS_MAPPINGS = {
    "TextAppendNode": TextAppendNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextAppendNode": "Text Append"
}
