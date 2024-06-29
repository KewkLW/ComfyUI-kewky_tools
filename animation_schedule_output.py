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
            }
        }

    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_string",)
    FUNCTION = "format_text"

    @torch.inference_mode()
    def format_text(self, unformatted_prompts, keyframe_interval, offset=0):
        # Reset the current_keyframe to 0 or to the offset at the start of each call
        self.current_keyframe = offset

        if not unformatted_prompts:
            return ["No input provided."]  # Return a list with a single string

        # Split the unformatted_prompts into lines
        lines = unformatted_prompts.split("\n")

        formatted_prompts = []
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                formatted_prompt = f'"{self.current_keyframe}" : "{line}"'
                self.current_keyframe += keyframe_interval
                formatted_prompts.append(formatted_prompt)

        # Join the formatted prompts with commas, except for the last one
        formatted_output = ",\n".join(formatted_prompts[:-1]) + ",\n" + formatted_prompts[-1] if formatted_prompts else ""

        print("Debug Final Output:", formatted_output)  # Debugging output to verify

        return [formatted_output]  # Return the formatted string wrapped in a list

NODE_CLASS_MAPPINGS = {
    "FormattedPromptNode": FormattedPromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FormattedPromptNode": "Animation Schedule Output",
}