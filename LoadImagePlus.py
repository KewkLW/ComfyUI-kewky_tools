import os
import hashlib
import random
import imghdr
import numpy as np
from PIL import Image, ImageOps, ImageSequence
import torch
from server import folder_paths 

class LoadImagePlus:
    def __init__(self):
        self.img_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()  # Ensure this method is correct
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "use_random_image": ("BOOLEAN", {"default": False}),
                "random_folder": ("STRING", {"default": "."}),
                "n_images": ("INT", {"default": 1, "min": 1, "max": 100}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 100000}),
                "sort": ("BOOLEAN", {"default": False}),
                "loop_sequence": ("BOOLEAN", {"default": False}),
            }
        }

    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "
    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"

    def load_image(self, image, use_random_image, random_folder, n_images, seed, sort, loop_sequence):
        if use_random_image:
            output_image, output_mask = self.load_random_image(random_folder, n_images, seed, sort, loop_sequence)
        else:
            output_image, output_mask = self.load_specific_image(image)
        return (output_image, output_mask)

    def load_specific_image(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)
        
        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']
        
        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]
            
            if image.size[0] != w or image.size[1] != h:
                continue
            
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

    def load_random_image(self, folder, n_images, seed, sort, loop_sequence):
        files = [os.path.join(folder, f) for f in os.listdir(folder)]
        files = [f for f in files if os.path.isfile(f)]
        files = [f for f in files if any([f.endswith(ext) for ext in self.img_extensions])]
        files = [f for f in files if imghdr.what(f)]

        random.seed(seed)
        random.shuffle(files)

        image_paths = files[:n_images]

        if sort:
            image_paths = sorted(image_paths)

        imgs = [Image.open(image_path) for image_path in image_paths]
        output_images = []
        for img in imgs:
            img = ImageOps.exif_transpose(img)
            if img.mode == 'I':
                img = img.point(lambda i: i * (1 / 255))
            image = img.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            output_images.append(image)

        if loop_sequence:
            output_images.append(output_images[0])

        if len(output_images) > 1:
            output_images = [torch.from_numpy(output_image)[None,] for output_image in output_images]
            output_image = torch.cat(output_images, dim=0)
        else:
            output_image = torch.from_numpy(output_images[0])[None,]

        # Create a dummy mask
        mask = torch.zeros((output_image.shape[0], 64, 64), dtype=torch.float32, device="cpu")

        return (output_image, mask)

    @classmethod
    def IS_CHANGED(cls, image, use_random_image, random_folder, n_images, seed, sort, loop_sequence):
        if use_random_image:
            return seed  # Return seed to indicate change when using random images
        else:
            image_path = folder_paths.get_annotated_filepath(image)
            m = hashlib.sha256()
            with open(image_path, 'rb') as f:
                m.update(f.read())
            return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, image, use_random_image, random_folder, n_images, seed, sort, loop_sequence):
        if not use_random_image:
            if not folder_paths.exists_annotated_filepath(image):
                return "Invalid image file: {}".format(image)
        else:
            if not os.path.isdir(random_folder):
                return "Invalid folder path: {}".format(random_folder)
        return True


NODE_CLASS_MAPPINGS = {
    "LoadImagePlus": LoadImagePlus
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImagePlus": "Load Image Plus"
}