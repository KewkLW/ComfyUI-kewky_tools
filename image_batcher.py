import os
import torch
import numpy as np
from PIL import Image
import gc
import psutil
import shutil

class ImageBatcher:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 9001}),
                "output_dir": ("STRING", {"default": "batch_output"}),
                "use_webp": ("BOOLEAN", {"default": False}),
                "webp_lossless": ("BOOLEAN", {"default": False}),
                "webp_quality": ("INT", {"default": 80, "min": 1, "max": 100}),
                "clear_dir": ("BOOLEAN", {"default": False})
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"}
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("images", "image_count", "batch_count", "debug_info")
    FUNCTION = "process_images"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def __init__(self):
        self.image_count = "0"
        self.batch_count = "0"
        self.debug_info = ""

    def process_images(self, images, batch_size, output_dir, use_webp, webp_lossless, webp_quality, clear_dir, prompt=None, extra_pnginfo=None):
        self.image_count = "0"
        self.batch_count = "0"
        self.debug_info = ""
        
        if clear_dir and os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        os.makedirs(output_dir, exist_ok=True)
        file_extension = ".webp" if use_webp else ".png"

        # Save images to disk and clear from memory
        for i, img in enumerate(images):
            img_np = (img.cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np)
            
            file_path = os.path.join(output_dir, f"image_{i:04d}{file_extension}")
            
            if use_webp:
                pil_img.save(file_path, format="WEBP", lossless=webp_lossless, quality=webp_quality)
            else:
                pil_img.save(file_path)
            
            del img_np, pil_img
            self.image_count = str(int(self.image_count) + 1)

            # Update the count in the prompt if available
            if prompt is not None:
                prompt["image_count"] = self.image_count
            
            # Update the count in extra_pnginfo if available
            if extra_pnginfo is not None:
                extra_pnginfo["image_count"] = self.image_count
        
        # Clear the original images from memory
        del images
        torch.cuda.empty_cache()
        gc.collect()

        # Get list of saved image files
        image_files = sorted([f for f in os.listdir(output_dir) if f.endswith(file_extension)])

        # Load images in batches
        batched_images = []
        for i in range(0, len(image_files), batch_size):
            batch = image_files[i:i+batch_size]
            for f in batch:
                img = Image.open(os.path.join(output_dir, f))
                img_tensor = torch.from_numpy(np.array(img).astype(np.float32) / 255.0)
                batched_images.append(img_tensor)
            
            # Increment batch count
            self.batch_count = str(int(self.batch_count) + 1)
            
            # Clear batch from memory if not the last batch
            if i + batch_size < len(image_files):
                del batch
                gc.collect()

        # Stack the batched images
        result = torch.stack(batched_images)
        
        # Clear individual tensors from memory
        del batched_images
        gc.collect()

        # Prepare debug info
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        gpu_memory_allocated = torch.cuda.memory_allocated() / 1e9

        self.debug_info = f"Total images: {self.image_count}\n"
        self.debug_info += f"Batch size: {batch_size}\n"
        self.debug_info += f"Number of batches: {self.batch_count}\n"
        self.debug_info += f"Shape of result tensor: {result.shape}\n"
        self.debug_info += f"CPU Memory usage: {memory_info.rss / 1e9:.2f} GB\n"
        self.debug_info += f"GPU Memory usage: {gpu_memory_allocated:.2f} GB"

        return (result, self.image_count, self.batch_count, self.debug_info)

NODE_CLASS_MAPPINGS = {
    "ImageBatcher": ImageBatcher
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBatcher": "Image Batcher"
}