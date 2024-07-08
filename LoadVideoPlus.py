import os
import hashlib
import random
import numpy as np
from PIL import Image, ImageOps
import torch
import cv2
from server import folder_paths

class LoadVideoPlus:
    def __init__(self):
        self.vid_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("IMAGE", ("STRING", {"default": "X:/insert/path/here.mp4"})),
                "use_random_video": ("BOOLEAN", {"default": False}),
                "random_folder": ("STRING", {"default": "."}),
                "n_videos": ("INT", {"default": 1, "min": 1, "max": 10}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 100000}),
                "sort": ("BOOLEAN", {"default": False}),
                "loop_sequence": ("BOOLEAN", {"default": False}),
            }
        }

    CATEGORY = "🧔🏻‍♂️🇰 🇪 🇼 🇰 "
    RETURN_TYPES = ("IMAGE", "MASK", "INT")
    RETURN_NAMES = ("output_video", "output_mask", "frame_count")
    FUNCTION = "load_video"

    def load_video(self, video, use_random_video, random_folder, n_videos, seed, sort, loop_sequence):
        if use_random_video:
            output_video, output_mask, frame_count = self.load_random_video(random_folder, n_videos, seed, sort, loop_sequence)
        else:
            output_video, output_mask, frame_count = self.load_specific_video(video)
        return (output_video, output_mask, frame_count)

    def load_specific_video(self, video):
        video_path = folder_paths.get_annotated_filepath(video) if hasattr(folder_paths, 'get_annotated_filepath') else video
        cap = cv2.VideoCapture(video_path)
        
        output_frames = []
        w, h = None, None
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = ImageOps.exif_transpose(Image.fromarray(frame))
            frame = np.array(frame).astype(np.float32) / 255.0

            if w is None and h is None:
                w, h = frame.shape[1], frame.shape[0]

            if frame.shape[1] != w or frame.shape[0] != h:
                continue
            
            frame = torch.from_numpy(frame)[None,]
            output_frames.append(frame)
            frame_count += 1

        cap.release()
        
        if not output_frames:
            raise ValueError("No frames were extracted from the video.")

        if len(output_frames) > 1:
            output_video = torch.cat(output_frames, dim=0)
        else:
            output_video = output_frames[0]

        # Create a dummy mask
        output_mask = torch.zeros((output_video.shape[0], 64, 64), dtype=torch.float32, device="cpu")

        return (output_video, output_mask, frame_count)

    def load_random_video(self, folder, n_videos, seed, sort, loop_sequence):
        files = [os.path.join(folder, f) for f in os.listdir(folder)]
        files = [f for f in files if os.path.isfile(f)]
        files = [f for f in files if any([f.endswith(ext) for ext in self.vid_extensions])]

        random.seed(seed)
        random.shuffle(files)

        video_paths = files[:n_videos]

        if sort:
            video_paths = sorted(video_paths)

        frames_list = []
        frame_count = 0

        for video_path in video_paths:
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = ImageOps.exif_transpose(Image.fromarray(frame))
                frame = np.array(frame).astype(np.float32) / 255.0
                frames_list.append(frame)
                frame_count += 1

            cap.release()

        if not frames_list:
            raise ValueError("No frames were extracted from the video(s).")

        if loop_sequence:
            frames_list.append(frames_list[0])
            frame_count += 1

        if len(frames_list) > 1:
            frames_list = [torch.from_numpy(frame)[None,] for frame in frames_list]
            output_video = torch.cat(frames_list, dim=0)
        else:
            output_video = torch.from_numpy(frames_list[0])[None,]

        # Create a dummy mask
        mask = torch.zeros((output_video.shape[0], 64, 64), dtype=torch.float32, device="cpu")

        return (output_video, mask, frame_count)

    @classmethod
    def IS_CHANGED(cls, video, use_random_video, random_folder, n_videos, seed, sort, loop_sequence):
        if use_random_video:
            return seed  # Return seed to indicate change when using random videos
        else:
            video_path = folder_paths.get_annotated_filepath(video) if hasattr(folder_paths, 'get_annotated_filepath') else video
            m = hashlib.sha256()
            with open(video_path, 'rb') as f:
                m.update(f.read())
            return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, video, use_random_video, random_folder, n_videos, seed, sort, loop_sequence):
        if not use_random_video:
            if not os.path.isfile(video):
                return "Invalid video file: {}".format(video)
        else:
            if not os.path.isdir(random_folder):
                return "Invalid folder path: {}".format(random_folder)
        return True

NODE_CLASS_MAPPINGS = {
    "LoadVideoPlus": LoadVideoPlus
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadVideoPlus": "Load Video Plus"
}