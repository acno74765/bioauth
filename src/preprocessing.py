# src/preprocessing.py

import cv2
import numpy as np
#preprocessing 
def gabor_filter_bank(kernel_size=21, sigma=5.0, theta_values=[0, np.pi/4, np.pi/2, 3*np.pi/4], lambd=10.0, gamma=0.5):
    """Create a Gabor filter bank with different orientations."""
    filters = []
    for theta in theta_values:
        kernel = cv2.getGaborKernel((kernel_size, kernel_size), sigma, theta, lambd, gamma, 0, ktype=cv2.CV_32F)
        filters.append(kernel)
    return filters

def apply_gabor_filters(image, filters):
    """Apply Gabor filters to the image to extract features."""
    features = []
    for kernel in filters:
        filtered_image = cv2.filter2D(image, cv2.CV_8UC3, kernel)
        features.append(np.mean(filtered_image))  # Feature representation using mean of the filtered image
    return np.array(features)

# Finger Code Extraction
def extract_fingercode_features(image, num_sectors=160, gabor_filters=None):
    """
    Extract a 640-dimensional feature vector from the fingerprint image.
    This is done by dividing the image into sectors and applying Gabor filters.
    """
    if gabor_filters is None:
        gabor_filters = gabor_filter_bank()
    
    # Resize the image to a standard size, e.g., 128x128
    resized_image = cv2.resize(image, (128, 128))
    
    # Divide the image into sectors
    sector_size = int(resized_image.shape[0] / np.sqrt(num_sectors))
    features = []
    
    # Loop through the sectors
    for i in range(0, resized_image.shape[0], sector_size):
        for j in range(0, resized_image.shape[1], sector_size):
            # Extract the current sector
            sector = resized_image[i:i + sector_size, j:j + sector_size]
            
            # Apply Gabor filters to the sector
            sector_features = apply_gabor_filters(sector, gabor_filters)
            
            # Add the features of the sector to the overall feature list
            features.extend(sector_features)
            
            # Stop if we reach 640 features
            if len(features) >= 640:
                break
        if len(features) >= 640:
            break
    
    # Flatten the features list and ensure it's 640-dimensional
    features = np.array(features).flatten()[:640]  # Truncate or pad to 640 dimensions if necessary
    if features.shape[0] < 640:
        features = np.pad(features, (0, 640 - features.shape[0]), 'constant')
    
    return features


# Load preprocessed image 
def load_and_preprocess_image(image_path):
    """Load a fingerprint image, preprocess, and enhance it."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Image not found at path: {image_path}")

    # Apply GaussianBlur to reduce noise
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)

    # Enhance the image using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_image = clahe.apply(blurred_image)

    return enhanced_image
