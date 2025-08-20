"""
Screenshot capture module for Tap Ninja Helper.
Handles capturing screenshots of specified areas of the screen.
"""

import time
import threading
from typing import Tuple, Optional

import pyautogui
import numpy as np
from PIL import Image, ImageGrab
import mss
import mss.tools

class ScreenCapture:
    """Screen capture manager class"""
    
    def __init__(self, use_mss: bool = True):
        """
        Initialize the screen capture manager.
        
        Args:
            use_mss: Whether to use MSS library (faster) or fall back to PyAutoGUI
        """
        self.use_mss = use_mss
        # Using thread-local storage for MSS to prevent threading issues
        self._thread_local = threading.local()
        self._thread_local.sct = mss.mss() if use_mss else None
    
    def _get_mss_instance(self):
        """Get or create a thread-local MSS instance"""
        if not hasattr(self._thread_local, 'sct') or self._thread_local.sct is None:
            self._thread_local.sct = mss.mss()
        return self._thread_local.sct
        
    def capture_area(self, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        """
        Capture a specific area of the screen.
        
        Args:
            x1: Left x-coordinate
            y1: Top y-coordinate
            x2: Right x-coordinate
            y2: Bottom y-coordinate
            
        Returns:
            PIL Image of the captured area
        """
        try:
            if self.use_mss:
                return self._capture_with_mss(x1, y1, x2, y2)
            else:
                return self._capture_with_pyautogui(x1, y1, x2, y2)
        except Exception as e:
            print(f"Screenshot error: {str(e)}")
            # Fall back to PyAutoGUI if MSS fails
            if self.use_mss:
                print("Falling back to PyAutoGUI for this capture")
                return self._capture_with_pyautogui(x1, y1, x2, y2)
            else:
                raise  # Re-raise if PyAutoGUI is already failing
    
    def _capture_with_mss(self, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        """Capture screenshot using MSS library (faster)"""
        width = x2 - x1
        height = y2 - y1
        
        # Get thread-local MSS instance
        sct = self._get_mss_instance()
        
        monitor = {"top": y1, "left": x1, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        
        # Convert to PIL Image
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    def _capture_with_pyautogui(self, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        """Capture screenshot using PyAutoGUI"""
        width = x2 - x1
        height = y2 - y1
        
        # PyAutoGUI uses top-left corner and size
        return pyautogui.screenshot(region=(x1, y1, width, height))
    
    def close(self):
        """Clean up resources"""
        try:
            if hasattr(self._thread_local, 'sct') and self._thread_local.sct is not None:
                self._thread_local.sct.close()
                self._thread_local.sct = None
        except Exception as e:
            print(f"Error closing MSS: {str(e)}")
