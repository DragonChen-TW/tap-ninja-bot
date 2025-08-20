"""
OCR module for Tap Ninja Helper.
Handles extracting text from images using Tesseract OCR.
"""

import os
from typing import Optional, Dict, Any, List, Union

import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance

class TextRecognition:
    """OCR text recognition manager class"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize the OCR text recognition manager.
        
        Args:
            tesseract_path: Path to Tesseract OCR executable. If None, uses default.
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Check if Tesseract is accessible
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            print(f"Warning: Could not initialize Tesseract OCR: {str(e)}")
            print("Make sure Tesseract is installed and the path is correct.")
            print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> np.ndarray:
        """
        Preprocess the image to improve OCR accuracy.
        
        Args:
            image: PIL Image or OpenCV image to preprocess
            
        Returns:
            Preprocessed OpenCV image
        """
        # Convert PIL Image to OpenCV format if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Apply dilation and erosion to enhance text regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        eroded = cv2.erode(dilated, kernel, iterations=1)
        
        # Invert back to black text on white background for OCR
        processed = cv2.bitwise_not(eroded)
        
        return processed
    
    def extract_text(self, image: Union[Image.Image, np.ndarray], preprocess: bool = True) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image: PIL Image or OpenCV image to extract text from
            preprocess: Whether to preprocess the image before OCR
            
        Returns:
            Extracted text as string
        """
        if preprocess:
            processed_image = self.preprocess_image(image)
        else:
            if isinstance(image, Image.Image):
                processed_image = np.array(image)
            else:
                processed_image = image
        
        # Configure Tesseract to focus on digits and simple text
        config = '--oem 3 --psm 6 -c tessedit_char_whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-%$,.:"'
        
        # Extract text
        text = pytesseract.image_to_string(processed_image, config=config).strip()
        
        return text
    
    def extract_numbers(self, image: Union[Image.Image, np.ndarray], preprocess: bool = True) -> List[float]:
        """
        Extract numbers from an image using OCR.
        
        Args:
            image: PIL Image or OpenCV image to extract numbers from
            preprocess: Whether to preprocess the image before OCR
            
        Returns:
            List of extracted numbers as floats
        """
        text = self.extract_text(image, preprocess)
        
        # Find all numbers in the text
        import re
        number_pattern = r'[-+]?\d*\.\d+|\d+'
        numbers = re.findall(number_pattern, text)
        
        # Convert to floats
        return [float(num) for num in numbers]
