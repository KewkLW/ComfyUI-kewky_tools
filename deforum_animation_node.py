import torch
import numpy as np
import torch.nn.functional as F

class DeforumAnimationNode:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": ("CONDITIONING", {"multiline": True}),
                "negative": ("CONDITIONING", {"multiline": True}),
                "latent": ("LATENT",),
                "angle": ("STRING", {"default": "0: (0)"}),
                "zoom": ("STRING", {"default": "0: (1.0)"}),
                "translation_x": ("STRING", {"default": "0: (0)"}),
                "translation_y": ("STRING", {"default": "0: (0)"}),
                "current_frame": ("INT", {"default": 0, "min": 0, "max": 9999}),
            },
        }

    RETURN_TYPES = ("LATENT", "CONDITIONING", "CONDITIONING")
    RETURN_NAMES = ("LATENT", "POSITIVE", "NEGATIVE")
    FUNCTION = "animate"
    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "
    
    def animate(self, positive, negative, latent, angle, zoom, translation_x, translation_y, current_frame):
        # Parse the frame schedules
        angle_value = self.parse_frame_schedule(angle, current_frame)
        zoom_value = self.parse_frame_schedule(zoom, current_frame)
        tx_value = self.parse_frame_schedule(translation_x, current_frame)
        ty_value = self.parse_frame_schedule(translation_y, current_frame)

        modified_latent = self.transform_latent(latent, angle_value, zoom_value, tx_value, ty_value)
        return (modified_latent, positive, negative)

    def parse_frame_schedule(self, schedule, frame):
        schedule_dict = {}
        for item in schedule.split(','):
            key, value = item.split(':')
            schedule_dict[int(key.strip())] = eval(value.strip())
        
        applicable_keyframes = [k for k in schedule_dict.keys() if k <= frame]
        if not applicable_keyframes:
            return schedule_dict[0] if 0 in schedule_dict else 0
        last_keyframe = max(applicable_keyframes)
        return schedule_dict[last_keyframe]

    def transform_latent(self, latent, angle, zoom, tx, ty):
        x = latent['samples']
        
        # Center the image for rotation and zoom
        center = torch.tensor((x.shape[3] / 2, x.shape[2] / 2)).to(x.device)
        center_mat = torch.eye(3).to(x.device)
        center_mat[:2, 2] = -center
        center_mat_inv = torch.eye(3).to(x.device)
        center_mat_inv[:2, 2] = center

        # Rotation matrix
        angle_rad = angle * np.pi / 180
        rotation_mat = torch.eye(3).to(x.device)
        rotation_mat[0, 0] = rotation_mat[1, 1] = np.cos(angle_rad)
        rotation_mat[0, 1] = -np.sin(angle_rad)
        rotation_mat[1, 0] = np.sin(angle_rad)

        # Scale matrix
        scale_mat = torch.eye(3).to(x.device)
        scale_mat[0, 0] = scale_mat[1, 1] = zoom

        # Translation matrix
        translation_mat = torch.eye(3).to(x.device)
        translation_mat[0, 2] = tx
        translation_mat[1, 2] = ty

        # Combine transformations
        M = translation_mat @ center_mat_inv @ rotation_mat @ scale_mat @ center_mat
        
        # Apply transformation
        grid = F.affine_grid(M[:2].unsqueeze(0).repeat(x.shape[0], 1, 1), x.size(), align_corners=False)
        x = F.grid_sample(x, grid, align_corners=False, mode='bilinear')

        return {"samples": x}

NODE_CLASS_MAPPINGS = {
    "DeforumAnimationNode": DeforumAnimationNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DeforumAnimationNode": "Deforum Animation"
}