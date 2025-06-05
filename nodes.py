import torch
import numpy as np
from PIL import Image
from pathlib import Path
import os
import folder_paths

class AspectRatioLatentNode:
    """
    A ComfyUI node that creates an empty latent matching the closest aspect ratio
    from a predefined list based on input image or dimensions.
    """
    
    # Predefined aspect ratios from the training hyperparameters
    ASPECT_RATIOS = [
        (512, 2048, 0.25), (512, 1984, 0.26), (512, 1920, 0.27), (512, 1856, 0.28),
        (576, 1792, 0.32), (576, 1728, 0.33), (576, 1664, 0.35), (640, 1600, 0.4),
        (640, 1536, 0.42), (704, 1472, 0.48), (704, 1408, 0.5), (704, 1344, 0.52),
        (768, 1344, 0.57), (768, 1280, 0.6), (832, 1216, 0.68), (832, 1152, 0.72),
        (896, 1152, 0.78), (896, 1088, 0.82), (960, 1088, 0.88), (960, 1024, 0.94),
        (1024, 1024, 1.0), (1024, 960, 1.07), (1088, 960, 1.13), (1088, 896, 1.21),
        (1152, 896, 1.29), (1152, 832, 1.38), (1216, 832, 1.46), (1280, 768, 1.67),
        (1344, 768, 1.75), (1408, 704, 2.0), (1472, 704, 2.09), (1536, 640, 2.4),
        (1600, 640, 2.5), (1664, 576, 2.89), (1728, 576, 3.0), (1792, 576, 3.11),
        (1856, 512, 3.62), (1920, 512, 3.75), (1984, 512, 3.88), (2048, 512, 4.0)
    ]
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
            },
            "optional": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
            }
        }
    
    RETURN_TYPES = ("LATENT", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("latent", "width", "height", "aspect_ratio", "info")
    FUNCTION = "create_latent"
    CATEGORY = "Koala"
    
    def find_closest_aspect_ratio(self, target_ratio):
        """Find the closest aspect ratio from the predefined list."""
        min_diff = float('inf')
        closest = None
        
        for height, width, ratio in self.ASPECT_RATIOS:
            diff = abs(ratio - target_ratio)
            if diff < min_diff:
                min_diff = diff
                closest = (height, width, ratio)
        
        return closest
    
    def create_latent(self, batch_size, image=None, width=None, height=None):
        """Create an empty latent with dimensions matching the closest aspect ratio."""
        
        # Determine input dimensions
        if image is not None:
            # Get dimensions from image
            # ComfyUI images are in format [batch, height, width, channels]
            _, h, w, _ = image.shape
            input_width = w
            input_height = h
        else:
            # Use provided width and height
            if width is None or height is None:
                raise ValueError("Either an image or both width and height must be provided")
            input_width = width
            input_height = height
        
        # Calculate aspect ratio
        input_ratio = input_height / input_width
        
        # Find closest matching aspect ratio
        matched_height, matched_width, matched_ratio = self.find_closest_aspect_ratio(input_ratio)
        
        # Create empty latent
        # Latent dimensions are 1/8 of the image dimensions for SD models
        latent_height = matched_height // 8
        latent_width = matched_width // 8
        
        # Create the latent tensor
        latent = torch.zeros([batch_size, 4, latent_height, latent_width])
        
        # Create info string
        info = f"Input: {input_width}x{input_height} (AR: {input_ratio:.2f}) → Matched: {matched_width}x{matched_height} (AR: {matched_ratio:.2f})"
        
        return ({"samples": latent}, matched_width, matched_height, matched_ratio, info)







class SaveMeshAnywhere:
    """
    A ComfyUI node that saves a 3D mesh to any location on disk.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
                "save_path": ("STRING", {"default": "C:/output/model.glb"}),
                "file_format": (["glb", "obj", "ply", "stl", "3mf", "dae"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "save_mesh"
    CATEGORY = "Koala"
    OUTPUT_NODE = True

    def save_mesh(self, trimesh, save_path, file_format):
        # Make sure the directory exists
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        # Ensure the file has the correct extension
        if not save_path.lower().endswith(f".{file_format}"):
            save_path = f"{os.path.splitext(save_path)[0]}.{file_format}"

        # Save the mesh to the specified path
        trimesh.export(save_path, file_type=file_format)

        return (save_path,)
# Node registration for ComfyUI
NODE_CLASS_MAPPINGS = {
    "AspectRatioLatentNode": AspectRatioLatentNode,
    "SaveMeshAnywhere": SaveMeshAnywhere,
    # Add more nodes here as you create them

}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioLatentNode": "Koala Aspect Ratio Empty Latent",
    "SaveMeshAnywhere": "Koala Save 3D Mesh Anywhere",
    # Add more display names here

}