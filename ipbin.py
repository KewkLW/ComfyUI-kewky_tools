import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

class IPBin:
    def __init__(self):
        self.indices = []
        self.image_schedule = []
        self.weight_schedule = []
        self.imageBatch = []
        self.bigImageBatch = []
        self.noiseBatch = []
        self.bigNoiseBatch = []

    def length(self):
        return len(self.image_schedule)
    
    def add(self, image, big_image, noise, big_noise, image_index, frame_numbers, weights):
        frame_to_weight = {frame: weights[i] for i, frame in enumerate(frame_numbers)}
        try:
            index = self.indices.index(image_index)
        except ValueError:
            self.imageBatch.append(image)
            self.bigImageBatch.append(big_image)
            if noise is not None: self.noiseBatch.append(noise) 
            if big_noise is not None: self.bigNoiseBatch.append(big_noise)
            self.indices.append(image_index)
            index = self.indices.index(image_index)
        
        self.image_schedule.extend([index] * (frame_numbers[-1] + 1 - len(self.image_schedule)))
        self.weight_schedule.extend([0] * (frame_numbers[0] - len(self.weight_schedule)))
        self.weight_schedule.extend(frame_to_weight[frame] for frame in range(frame_numbers[0], frame_numbers[-1] + 1))

class IPAdapterBinPreprocessor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "images": ("IMAGE",),
                "keyframe_positions": ("STRING", {"default": "0,16,32,48"}),
                "weights": ("STRING", {"default": "1.0,1.0,1.0,1.0"}),
                "max_frames_per_bin": ("INT", {"default": 32, "min": 1, "max": 1000, "step": 1}),
                "high_detail_mode": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "base_ipa_advanced_settings": ("ADVANCED_IPA_SETTINGS",),
                "detail_ipa_advanced_settings": ("ADVANCED_IPA_SETTINGS",),
            }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "preprocess"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "

    def preprocess(self, model, images, keyframe_positions, weights, max_frames_per_bin, high_detail_mode, base_ipa_advanced_settings=None, detail_ipa_advanced_settings=None):
        bins = self.create_bins(images, keyframe_positions, weights, max_frames_per_bin, high_detail_mode, base_ipa_advanced_settings, detail_ipa_advanced_settings)
        
        if not hasattr(model, 'ip_adapter_bins'):
            model.ip_adapter_bins = []
        model.ip_adapter_bins.append(bins)
        
        return (model,)

    def create_bins(self, images, keyframe_positions, weights, max_frames_per_bin, high_detail_mode, base_ipa_advanced_settings, detail_ipa_advanced_settings):
        keyframe_positions = [int(pos) for pos in keyframe_positions.split(',')]
        weights = [float(w) for w in weights.split(',')]
        
        bins = [IPBin()]
        
        for i, (position, weight) in enumerate(zip(keyframe_positions, weights)):
            if i == 0:
                continue  # Skip the first keyframe as it's usually just a buffer
            
            image = images[i-1]
            image_index = i-1
            
            if i < len(keyframe_positions) - 1:
                frame_numbers = range(position, keyframe_positions[i+1])
            else:
                frame_numbers = range(position, position + max_frames_per_bin)
            
            frame_weights = [weight] * len(frame_numbers)
            
            prepared_image, big_image = self.prepare_images(image, base_ipa_advanced_settings, detail_ipa_advanced_settings)
            
            base_noise = self.prepare_noise(prepared_image, base_ipa_advanced_settings) if base_ipa_advanced_settings else None
            detail_noise = self.prepare_noise(big_image, detail_ipa_advanced_settings) if high_detail_mode and detail_ipa_advanced_settings else None
            
            suitable_bin = None
            for bin in bins:
                if bin.length() + len(frame_numbers) <= max_frames_per_bin:
                    suitable_bin = bin
                    break
            
            if suitable_bin is None:
                suitable_bin = IPBin()
                bins.append(suitable_bin)
            
            suitable_bin.add(prepared_image, big_image, base_noise, detail_noise, image_index, frame_numbers, frame_weights)
        
        return bins
    
    def prepare_images(self, image, base_settings, detail_settings):
        prepared_image = transforms.functional.to_tensor(image).unsqueeze(0)
        big_image = image.unsqueeze(0) if detail_settings else None
        return prepared_image, big_image
    
    def prepare_noise(self, image, settings):
        if settings and settings.get("ipa_noise_strength", 0) > 0:
            return torch.randn_like(image) * settings["ipa_noise_strength"]
        return None

class IPAdapterBinApply:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "ipadapter": ("IPADAPTER",),
                "clip_vision": ("CLIP_VISION",),
                "high_detail_mode": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "base_ipa_advanced_settings": ("ADVANCED_IPA_SETTINGS",),
                "detail_ipa_advanced_settings": ("ADVANCED_IPA_SETTINGS",),
            }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "apply"
    CATEGORY = "IPAdapter"

    def apply(self, model, ipadapter, clip_vision, high_detail_mode, base_ipa_advanced_settings=None, detail_ipa_advanced_settings=None):
        if not hasattr(model, 'ip_adapter_bins') or not model.ip_adapter_bins:
            raise ValueError("No IPAdapter bins found in the model. Please run IPAdapterBinPreprocessor first.")
        
        bins = model.ip_adapter_bins.pop(0)
        
        for bin in bins:
            ipadapter_application = IPAdapterBatchImport()
            model, _ = ipadapter_application.apply_ipadapter(
                model=model,
                ipadapter=ipadapter,
                image=torch.cat(bin.imageBatch, dim=0),
                weight=[w * base_ipa_advanced_settings.get("ipa_weight", 1.0) for w in bin.weight_schedule],
                weight_type=base_ipa_advanced_settings.get("ipa_weight_type", "linear"),
                start_at=base_ipa_advanced_settings.get("ipa_starts_at", 0.0),
                end_at=base_ipa_advanced_settings.get("ipa_ends_at", 1.0),
                clip_vision=clip_vision,
                image_negative=torch.cat(bin.noiseBatch, dim=0) if bin.noiseBatch else None,
                embeds_scaling=base_ipa_advanced_settings.get("ipa_embeds_scaling", "V only"),
                encode_batch_size=1,
                image_schedule=bin.image_schedule
            )
            
            if high_detail_mode and detail_ipa_advanced_settings:
                tiled_ipa_application = IPAdapterTiledBatchImport()
                model, _ = tiled_ipa_application.apply_tiled(
                    model=model,
                    ipadapter=ipadapter,
                    image=torch.cat(bin.bigImageBatch, dim=0),
                    weight=[w * detail_ipa_advanced_settings.get("ipa_weight", 1.0) for w in bin.weight_schedule],
                    weight_type=detail_ipa_advanced_settings.get("ipa_weight_type", "linear"),
                    start_at=detail_ipa_advanced_settings.get("ipa_starts_at", 0.0),
                    end_at=detail_ipa_advanced_settings.get("ipa_ends_at", 1.0),
                    clip_vision=clip_vision,
                    image_negative=torch.cat(bin.bigNoiseBatch, dim=0) if bin.bigNoiseBatch else None,
                    embeds_scaling=detail_ipa_advanced_settings.get("ipa_embeds_scaling", "V only"),
                    encode_batch_size=1,
                    image_schedule=bin.image_schedule
                )
        
        return (model,)

# Node mappings
NODE_CLASS_MAPPINGS = {
    "IPAdapterBinPreprocessor": IPAdapterBinPreprocessor,
    "IPAdapterBinApply": IPAdapterBinApply,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IPAdapterBinPreprocessor": "IPAdapter Bin Preprocessor 🎞️🅢🅜",
    "IPAdapterBinApply": "IPAdapter Bin Apply 🎞️🅢🅜",
}