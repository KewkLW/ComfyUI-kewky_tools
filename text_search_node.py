import os
import json
import yaml
from glob import glob

class TextSearchNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": False}),
                "location": ("STRING", {"multiline": False}),
                "search_in_files": ("BOOLEAN", {"default": True}),
                "search_in_filenames": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "txt": ("BOOLEAN", {"default": False}),
                "py": ("BOOLEAN", {"default": False}),
                "md": ("BOOLEAN", {"default": False}),
                "yaml": ("BOOLEAN", {"default": False}),
                "yml": ("BOOLEAN", {"default": False}),
                "json": ("BOOLEAN", {"default": False}),
                "js": ("BOOLEAN", {"default": False})
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "search_text"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def search_text(self, text, location, search_in_files, search_in_filenames, txt=False, py=False, md=False, yaml=False, yml=False, json=False, js=False):
        result = []
        extensions = []
        if txt: extensions.append("txt")
        if py: extensions.append("py")
        if md: extensions.append("md")
        if yaml: extensions.append("yaml")
        if yml: extensions.append("yml")
        if json: extensions.append("json")
        if js: extensions.append("js")

        for ext in extensions:
            for file_path in glob(os.path.join(location, f"**/*.{ext}"), recursive=True):
                if search_in_filenames and text.lower() in os.path.basename(file_path).lower():
                    result.append(f"Found in filename: {file_path}")

                if search_in_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            if ext in ['yaml', 'yml']:
                                content = yaml.safe_load(file)
                                if self.search_in_yaml(text, content):
                                    result.append(f"Found in YAML content: {file_path}")
                            elif ext == 'json':
                                content = json.load(file)
                                if self.search_in_json(text, content):
                                    result.append(f"Found in JSON content: {file_path}")
                            else:
                                if text.lower() in file.read().lower():
                                    result.append(f"Found in file content: {file_path}")
                    except Exception as e:
                        result.append(f"Error processing {file_path}: {str(e)}")

        return ("\n".join(result),)

    def search_in_yaml(self, text, content):
        if isinstance(content, dict):
            return any(self.search_in_yaml(text, value) for value in content.values())
        elif isinstance(content, list):
            return any(self.search_in_yaml(text, item) for item in content)
        else:
            return text.lower() in str(content).lower()

    def search_in_json(self, text, content):
        if isinstance(content, dict):
            return any(self.search_in_json(text, value) for value in content.values())
        elif isinstance(content, list):
            return any(self.search_in_json(text, item) for item in content)
        else:
            return text.lower() in str(content).lower()

NODE_CLASS_MAPPINGS = {
    "TextSearchNode": TextSearchNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextSearchNode": "Text Search"
}