"""
Windows environment test for Tap Ninja Helper.
Tests that the required components are installed and working correctly.
"""

import os
import sys
import time
import tkinter as tk
from tkinter import messagebox

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.capture.screenshot import ScreenCapture
from src.ocr.text_recognition import TextRecognition


def test_tesseract():
    """Test that Tesseract OCR is installed and working"""
    print("Testing Tesseract OCR...")
    
    config = Config()
    tesseract_path = config.get_tesseract_path()
    
    if not os.path.exists(tesseract_path):
        print(f"ERROR: Tesseract OCR not found at {tesseract_path}")
        print("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    # Try to initialize Tesseract
    try:
        ocr = TextRecognition(tesseract_path)
        print("✓ Tesseract OCR is installed and configured correctly")
        return True
    except Exception as e:
        print(f"ERROR: Could not initialize Tesseract OCR: {str(e)}")
        return False


def test_screenshot():
    """Test that screenshot capture is working"""
    print("Testing screenshot capture...")
    
    try:
        # Try both screenshot methods
        print("Testing MSS screenshot...")
        mss_capture = ScreenCapture(use_mss=True)
        mss_screenshot = mss_capture.capture_area(0, 0, 200, 200)
        
        print("Testing PyAutoGUI screenshot...")
        pyautogui_capture = ScreenCapture(use_mss=False)
        pyautogui_screenshot = pyautogui_capture.capture_area(0, 0, 200, 200)
        
        # Clean up
        mss_capture.close()
        
        print("✓ Screenshot capture is working with both methods")
        return True
    except Exception as e:
        print(f"ERROR: Screenshot capture failed: {str(e)}")
        return False


def test_ui():
    """Test that Tkinter UI is working"""
    print("Testing Tkinter UI...")
    
    try:
        # Try to create a Tk window
        root = tk.Tk()
        root.title("UI Test")
        root.geometry("300x200")
        
        # Add a label
        label = tk.Label(root, text="Tkinter UI is working!")
        label.pack(pady=50)
        
        # Set up a timer to close the window after 2 seconds
        root.after(2000, root.destroy)
        
        # Start main loop
        root.mainloop()
        
        print("✓ Tkinter UI is working")
        return True
    except Exception as e:
        print(f"ERROR: Tkinter UI failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("Running Windows environment tests for Tap Ninja Helper...")
    print("=" * 60)
    
    # Test Tesseract
    tesseract_ok = test_tesseract()
    print("-" * 60)
    
    # Test screenshot
    screenshot_ok = test_screenshot()
    print("-" * 60)
    
    # Test UI
    ui_ok = test_ui()
    print("-" * 60)
    
    # Summary
    print("\nTest Summary:")
    print(f"Tesseract OCR: {'✓ OK' if tesseract_ok else '✗ Failed'}")
    print(f"Screenshot:    {'✓ OK' if screenshot_ok else '✗ Failed'}")
    print(f"Tkinter UI:    {'✓ OK' if ui_ok else '✗ Failed'}")
    
    if tesseract_ok and screenshot_ok and ui_ok:
        print("\n✓ All tests passed! The Windows environment is correctly set up.")
        return True
    else:
        print("\n✗ Some tests failed. Please fix the issues above before continuing.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
