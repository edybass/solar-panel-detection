"""Image preprocessing utilities for satellite imagery"""
import cv2
import numpy as np
import rasterio

def normalize_satellite_image(image_path):
    """Normalize satellite imagery for ML processing"""
    with rasterio.open(image_path) as src:
        # Read RGB bands
        red = src.read(1)
        green = src.read(2)
        blue = src.read(3)
        
        # Stack and normalize
        rgb = np.dstack((red, green, blue))
        rgb = np.clip(rgb / rgb.max() * 255, 0, 255).astype(np.uint8)
        
    return rgb

def create_patches(image, patch_size=256, overlap=0.2):
    """Create overlapping patches from large image"""
    h, w = image.shape[:2]
    step = int(patch_size * (1 - overlap))
    patches = []
    
    for y in range(0, h - patch_size + 1, step):
        for x in range(0, w - patch_size + 1, step):
            patch = image[y:y+patch_size, x:x+patch_size]
            if patch.shape[:2] == (patch_size, patch_size):
                patches.append(patch)
    
    return np.array(patches)
