import torch

class FormattedPromptNode:
    NODE_NAME = "Animation Schedule Output"
    current_keyframe = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unformatted_prompts": ("STRING", {"default": "", "multiline": True, "forceInput": True, "connectable": True}),
                "keyframe_interval": ("INT", {"default": 50, "min": 1, "max": 8192, "step": 1}),
            },
            "optional": {
                "offset": ("INT", {"default": 0, "min": 0}),
                "prepend_text": ("STRING", {"default": "", "multiline": True}),
                "append_text": ("STRING", {"default": "", "multiline": True}),
            }
        }

    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_string",)
    FUNCTION = "format_text"

    @torch.inference_mode()
    def format_text(self, unformatted_prompts, keyframe_interval, offset=0, prepend_text="", append_text=""):
        self.current_keyframe = offset

        if not unformatted_prompts and not prepend_text and not append_text:
            return ["No input provided."]

        formatted_prompts = []

        # Process main unformatted prompts
        if unformatted_prompts:
            lines = unformatted_prompts.split("\n")
            for line in lines:
                line = line.strip()
                if line:
                    # Add prepend text to each frame
                    if prepend_text:
                        formatted_prompt = f'"{self.current_keyframe}" : "{prepend_text.strip()}, {line}"'
                    else:
                        formatted_prompt = f'"{self.current_keyframe}" : "{line}"'
                    
                    # Add append text to each frame
                    if append_text:
                        formatted_prompt = formatted_prompt[:-1] + f", {append_text.strip()}\""
                    
                    self.current_keyframe += keyframe_interval
                    formatted_prompts.append(formatted_prompt)

        formatted_output = ",\n".join(formatted_prompts) if formatted_prompts else ""

        print("Debug Final Output:", formatted_output)  # Debugging output to verify

        return [formatted_output]

NODE_CLASS_MAPPINGS = {
    "FormattedPromptNode": FormattedPromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FormattedPromptNode": "Animation Schedule Output",
}