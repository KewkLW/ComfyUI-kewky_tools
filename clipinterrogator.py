import torch
import open_clip
from clip_interrogator import Config, Interrogator
from PIL import Image
import os
import numpy as np

class CLIPInterrogatorNode:
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.interrogator = None
        self.current_model = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "clip_model_name": (["ViT-L-14/openai", "ViT-H-14/laion2b_s32b_b79k", "ViT-bigG-14/laion2b_s39b", "OpenCLIP ViT-G/14"],),
                "mode": (["best", "fast", "classic", "negative"],),
                "save_text": ("BOOLEAN", {"default": False}),
                "keep_model_loaded": ("BOOLEAN", {"default": False}),
                "output_dir": ("STRING", {"default": "same as image"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "interrogate_image"
    RETURN_NAMES = ("text",)

    def load_interrogator(self, clip_model_name):
        if self.interrogator is None or clip_model_name != self.current_model:
            config = Config(
                clip_model_name=clip_model_name,
                device=self.device
            )
            self.interrogator = Interrogator(config)
            self.current_model = clip_model_name

    def unload_interrogator(self):
        if self.interrogator is not None:
            del self.interrogator
            self.interrogator = None
            self.current_model = None
            torch.cuda.empty_cache()

    def interrogate_image(self, image, clip_model_name, mode, save_text, keep_model_loaded, output_dir):
        if not self.validate_inputs(image, clip_model_name, mode, save_text, keep_model_loaded, output_dir):
            return ("Error: Invalid inputs",)

        self.load_interrogator(clip_model_name)

        try:
            results = []
            for i in range(image.shape[0]):  # Iterate over the batch
                # Convert the image to PIL Image using the new method
                pil_image = self.comfy_tensor_to_pil(image[i])
                
                # Use the interrogator's methods directly
                if mode == 'best':
                    result = self.interrogator.interrogate(pil_image)
                elif mode == 'fast':
                    result = self.interrogator.interrogate_fast(pil_image)
                elif mode == 'classic':
                    result = self.interrogator.interrogate_classic(pil_image)
                elif mode == 'negative':
                    result = self.interrogator.interrogate_negative(pil_image)
                else:
                    raise ValueError(f"Unknown mode: {mode}")

                results.append(result)

                if save_text:
                    self.save_text_file(f"image_{i}", result, output_dir, image[i])

            if not keep_model_loaded:
                self.unload_interrogator()

            # Join all prompts into a single string, separated by newlines
            combined_result = "\n".join(results)

            return (combined_result,)
        except Exception as e:
            print(f"Error in CLIP Interrogator: {str(e)}")
            return (f"Error: Unable to generate prompt. {str(e)}",)

    def comfy_tensor_to_pil(self, tensor):
        # Ensure the tensor is on CPU and detached from the computation graph
        tensor = tensor.cpu().detach()

        # Convert to numpy array
        image_np = tensor.numpy()

        # Ensure the image has 3 dimensions (H, W, C)
        if image_np.ndim != 3:
            raise ValueError(f"Unexpected image shape: {image_np.shape}")

        # If the image is grayscale, convert to RGB
        if image_np.shape[-1] == 1:
            image_np = np.repeat(image_np, 3, axis=-1)

        # Ensure the values are in the range [0, 255]
        if image_np.max() <= 1.0:
            image_np = (image_np * 255).astype(np.uint8)
        else:
            image_np = image_np.astype(np.uint8)

        # Create PIL Image
        return Image.fromarray(image_np)

    def save_text_file(self, image_name, prompt, output_dir, image):
        if output_dir == "same as image" or not output_dir:
            # Assume the image is from a "Load Image" node, which provides metadata
            if hasattr(image, 'already_saved_as'):
                output_dir = os.path.dirname(image.already_saved_as)
            else:
                output_dir = os.getcwd()  # Fallback to current working directory
        
        file_path = os.path.join(output_dir, f"{image_name}_prompt.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(prompt)

    def validate_inputs(self, image, clip_model_name, mode, save_text, keep_model_loaded, output_dir):
        if not isinstance(image, torch.Tensor):
            print(f"Invalid image input. Expected a torch.Tensor, got {type(image)}.")
            return False
        if clip_model_name not in ["ViT-L-14/openai", "ViT-H-14/laion2b_s32b_b79k", "ViT-bigG-14/laion2b_s39b", "OpenCLIP ViT-G/14"]:
            print("Invalid CLIP model name.")
            return False
        if mode not in ["best", "fast", "classic", "negative"]:
            print("Invalid interrogation mode.")
            return False
        if not isinstance(save_text, bool):
            print("Invalid save_text input. Expected a boolean.")
            return False
        if not isinstance(keep_model_loaded, bool):
            print("Invalid keep_model_loaded input. Expected a boolean.")
            return False
        if not isinstance(output_dir, str):
            print("Invalid output_dir input. Expected a string.")
            return False
        return True

NODE_CLASS_MAPPINGS = {
    "CLIPInterrogator": CLIPInterrogatorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPInterrogator": "CLIP Interrogator"
}