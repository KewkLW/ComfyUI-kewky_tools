import torch
import os
import comfy.utils
import comfy.sd
import folder_paths

class load_unet:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                             }}
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "load_unet"

    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def load_unet(self, ckpt_name):
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        sd = comfy.utils.load_torch_file(ckpt_path)
        
        # Extract only U-Net related weights
        unet_sd = {k: v for k, v in sd.items() if k.startswith("model.diffusion_model.")}
        
        # Load U-Net configuration (you might need to adjust this part based on your specific needs)
        from comfy.sd import load_model_config
        model_config = load_model_config(ckpt_path)
        
        # Initialize U-Net
        unet = comfy.sd.UNetModel(model_config)
        
        # Load weights into U-Net
        unet.load_state_dict(unet_sd)
        
        return (unet,)
    
NODE_CLASS_MAPPINGS = {
    "load_unet": load_unet
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "load_unet": "Load U-Net"
}