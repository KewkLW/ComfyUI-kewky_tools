import torch
import open_clip
from clip_interrogator import Config, Interrogator
from PIL import Image
import os
import numpy as np
import json
import hashlib

class CLIPInterrogatorNode:
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.interrogator = None
        self.current_model = None
        self.cache_path = os.path.join('models', 'clip-interrogator')
        self.embedding_directory = os.path.join('models', 'clip-interrogator', 'embeddings')
        self.cache_file = os.path.join(self.cache_path, 'interrogation_cache.json')
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def get_image_hash(self, image):
        return hashlib.md5(image.tobytes()).hexdigest()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "clip_model_name": (cls.get_clip_models(),),
                "pos": (["best", "fast", "classic", "negative"],),
                "neg": (["best", "fast", "classic", "negative"],),
                "save_text": ("BOOLEAN", {"default": False}),
                "keep_model_loaded": ("BOOLEAN", {"default": False}),
                "output_dir": ("STRING", {"default": "same as image"}),
                "use_precomputed": ("BOOLEAN", {"default": True}),
                "use_cache": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    FUNCTION = "interrogate_image"
    RETURN_NAMES = ("pos", "neg",)

    @classmethod
    def get_clip_models(cls):
        return [
            "ViT-L-14/openai",
            "ViT-H-14/laion2b_s32b_b79k",
            "ViT-bigG-14/laion2b_s39b",
            "ViT-B-32/laion2b_e16",
            "ViT-B-32/laion400m_e31",
            "ViT-B-32/laion400m_e32",
            "ViT-B-16/laion400m_e31",
            "ViT-B-16/laion400m_e32",
            "RN50/openai",
            "RN50-quickgelu/openai",
            "RN101/openai",
            "RN50x4/openai",
            "RN50x16/openai",
            "RN50x64/openai",
            "ViT-L-14/openai",
            "ViT-L-14-336/openai"
        ]

    def load_interrogator(self, clip_model_name, use_precomputed):
        if self.interrogator is None or clip_model_name != self.current_model:
            config = Config(
                clip_model_name=clip_model_name,
                device=self.device,
                cache_path=self.cache_path
            )
            self.interrogator = Interrogator(config)
            self.current_model = clip_model_name

            if use_precomputed:
                self.load_precomputed_embeddings(clip_model_name)

    def load_precomputed_embeddings(self, clip_model_name):
        embedding_files = {
            'artists': f'{clip_model_name.split("/")[0]}_artists.pt',
            'mediums': f'{clip_model_name.split("/")[0]}_mediums.pt',
            'movements': f'{clip_model_name.split("/")[0]}_movements.pt',
            'trendings': f'{clip_model_name.split("/")[0]}_trendings.pt',
            'flavors': 'flavors.pt'
        }

        for key, filename in embedding_files.items():
            path = os.path.join(self.embedding_directory, filename)
            if os.path.exists(path):
                embeddings = torch.load(path, map_location=self.device)
                setattr(self.interrogator, key, embeddings)
            else:
                print(f"Warning: Precomputed embedding file not found: {path}")

    def unload_interrogator(self):
        if self.interrogator is not None:
            del self.interrogator
            self.interrogator = None
            self.current_model = None
            torch.cuda.empty_cache()

    def interrogate_image(self, image, clip_model_name, pos, neg, save_text, keep_model_loaded, output_dir, use_precomputed, use_cache):
        if not self.validate_inputs(image, clip_model_name, pos, neg, save_text, keep_model_loaded, output_dir, use_precomputed, use_cache):
            return ("Error: Invalid inputs", "Error: Invalid inputs")

        results_1 = []
        results_2 = []

        for i in range(image.shape[0]):  # Iterate over the batch
            pil_image = self.comfy_tensor_to_pil(image[i])
            image_hash = self.get_image_hash(pil_image)
            
            cache_key_pos = f"{image_hash}_{clip_model_name}_{pos}"
            cache_key_neg = f"{image_hash}_{clip_model_name}_{neg}"

            if use_cache and cache_key_pos in self.cache and cache_key_neg in self.cache:
                result_1 = self.cache[cache_key_pos]
                result_2 = self.cache[cache_key_neg]
            else:
                self.load_interrogator(clip_model_name, use_precomputed)
                
                result_1 = self.process_mode(pil_image, pos)
                result_2 = self.process_mode(pil_image, neg)

                if use_cache:
                    self.cache[cache_key_pos] = result_1
                    self.cache[cache_key_neg] = result_2
                    self.save_cache()

            results_1.append(result_1)
            results_2.append(result_2)

            if save_text:
                self.save_text_file(f"image_{i}_output1", result_1, output_dir, image[i])
                self.save_text_file(f"image_{i}_output2", result_2, output_dir, image[i])

        if not keep_model_loaded:
            self.unload_interrogator()

        combined_result_1 = "\n".join(results_1)
        combined_result_2 = "\n".join(results_2)

        return (combined_result_1, combined_result_2)

    def process_mode(self, pil_image, mode):
        if mode == 'best':
            return self.interrogator.interrogate(pil_image)
        elif mode == 'fast':
            return self.interrogator.interrogate_fast(pil_image)
        elif mode == 'classic':
            return self.interrogator.interrogate_classic(pil_image)
        elif mode == 'negative':
            return self.interrogator.interrogate_negative(pil_image)
        else:
            raise ValueError(f"Unknown mode: {mode}")

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

    def validate_inputs(self, image, clip_model_name, pos, neg, save_text, keep_model_loaded, output_dir, use_precomputed, use_cache):
        if not isinstance(image, torch.Tensor):
            print(f"Invalid image input. Expected a torch.Tensor, got {type(image)}.")
            return False
        if clip_model_name not in self.get_clip_models():
            print("Invalid CLIP model name.")
            return False
        if pos not in ["best", "fast", "classic", "negative"] or neg not in ["best", "fast", "classic", "negative"]:
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
        if not isinstance(use_precomputed, bool):
            print("Invalid use_precomputed input. Expected a boolean.")
            return False
        if not isinstance(use_cache, bool):
            print("Invalid use_cache input. Expected a boolean.")
            return False
        return True

NODE_CLASS_MAPPINGS = {
    "CLIPInterrogator": CLIPInterrogatorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPInterrogator": "CLIP Interrogator"
}