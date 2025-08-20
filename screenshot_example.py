#!/usr/bin/env python3
"""
screenshot_example.py - Example implementation of screenshot functionality using MSS

This module demonstrates how to:
1. Capture screenshots from specific regions of the screen in WSL
2. Process the screenshots for OCR
3. Handle common WSL-specific issues

For Tap Ninja Helper project
"""

import time
import sys
import logging
from pathlib import Path
from typing import Tuple, Dict, Optional

import numpy as np
import cv2
from mss import mss
from PIL import Image, ImageEnhance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScreenCapture:
    """Screen capture utility using MSS library, optimized for WSL."""
    
    def __init__(self):
        """Initialize the screen capture utility."""
        try:
            # Check if we can access the display through X11
            self.sct = mss()
            logger.info(f"Screen capture initialized. Found {len(self.sct.monitors)} monitors.")
        except Exception as e:
            logger.error(f"Failed to initialize screen capture: {e}")
            logger.error("Make sure X server is running on Windows and DISPLAY is set to :0")
            sys.exit(1)
    
    def capture_area(self, 
                     left: int, 
                     top: int, 
                     width: int, 
                     height: int) -> Optional[np.ndarray]:
        """
        Capture a specific area of the screen.
        
        Args:
            left: Left coordinate of the capture area
            top: Top coordinate of the capture area
            width: Width of the capture area
            height: Height of the capture area
            
        Returns:
            numpy.ndarray: The captured image as a numpy array (BGR format)
            or None if capture failed
        """
        try:
            # Define the capture region
            monitor = {"left": left, "top": top, "width": width, "height": height}
            
            # Capture the specified area
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array (BGR format for OpenCV compatibility)
            img = np.array(screenshot)
            
            logger.debug(f"Screenshot captured: {width}x{height} at ({left}, {top})")
            return img
        
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def preprocess_for_ocr(self, image: np.ndarray) -> Image.Image:
        """
        Preprocess the captured image for better OCR results.
        
        Args:
            image: The captured image as numpy array
            
        Returns:
            PIL.Image: Preprocessed image ready for OCR
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black text on white background
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Convert to PIL Image for Tesseract
        pil_img = Image.fromarray(thresh)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        enhanced_img = enhancer.enhance(2.0)
        
        return enhanced_img
    
    def save_screenshot(self, 
                        image: np.ndarray, 
                        filepath: str = "screenshot.png") -> bool:
        """
        Save the screenshot to a file.
        
        Args:
            image: The image to save
            filepath: Path to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert BGR to RGB for proper color display
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)
            pil_img.save(filepath)
            logger.info(f"Screenshot saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False


def capture_every_n_seconds(left: int, 
                           top: int, 
                           width: int, 
                           height: int, 
                           interval: int = 5,
                           max_captures: int = 5) -> None:
    """
    Capture screenshots every n seconds from a specified area.
    
    Args:
        left: Left coordinate of the capture area
        top: Top coordinate of the capture area
        width: Width of the capture area
        height: Height of the capture area
        interval: Time between captures in seconds
        max_captures: Maximum number of captures to take
    """
    screen_capture = ScreenCapture()
    
    # Create output directory
    output_dir = Path("screenshots")
    output_dir.mkdir(exist_ok=True)
    
    for i in range(max_captures):
        # Capture screenshot
        img = screen_capture.capture_area(left, top, width, height)
        if img is not None:
            # Save the screenshot
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filepath = output_dir / f"screenshot_{timestamp}.png"
            screen_capture.save_screenshot(img, str(filepath))
            
            # Preprocess for OCR demonstration
            processed_img = screen_capture.preprocess_for_ocr(img)
            processed_filepath = output_dir / f"processed_{timestamp}.png"
            processed_img.save(str(processed_filepath))
            logger.info(f"Processed image saved to {processed_filepath}")
            
        # Wait for the next interval
        if i < max_captures - 1:
            logger.info(f"Waiting {interval} seconds for next capture...")
            time.sleep(interval)
    
    logger.info(f"Completed {max_captures} captures.")


if __name__ == "__main__":
    # Example usage - capture from a 400x100 area at position (100, 100)
    print("Tap Ninja Helper - Screenshot Example")
    print("=====================================")
    print("This will take 5 screenshots, one every 5 seconds")
    print("Make sure your X server is running on Windows")
    print("Screenshots will be saved in the 'screenshots' directory")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    # Capture area (adjust as needed)
    capture_every_n_seconds(
        left=100,    # X coordinate of top-left corner
        top=100,     # Y coordinate of top-left corner
        width=400,   # Width of the capture area
        height=100,  # Height of the capture area
        interval=5,  # Seconds between captures
        max_captures=5  # Total number of screenshots to take
    )
