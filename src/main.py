"""
Tap Ninja Helper - Main Entry Point
This is the main entry point for the Tap Ninja Helper application.
"""

import os
import sys
import tkinter as tk

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.dashboard import Dashboard
from src.config import Config
from src.ocr.text_recognition import TextRecognition


def check_environment():
    """Check that the environment is correctly set up"""
    try:
        # Check if Tesseract is installed
        config = Config()
        tesseract_path = config.get_tesseract_path()
        
        if not os.path.exists(tesseract_path):
            print(f"Warning: Tesseract OCR executable not found at {tesseract_path}")
            print("Please install Tesseract OCR and update the path in settings.")
            print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        else:
            # Try to initialize Tesseract
            ocr = TextRecognition(tesseract_path)
            print("Environment check passed. Tesseract OCR is available.")
            
        return True
        
    except Exception as e:
        print(f"Environment check failed: {str(e)}")
        return False


def main():
    """Main entry point"""
    print("Starting Tap Ninja Helper...")
    
    # Check environment
    if not check_environment():
        print("Warning: Environment check failed. Some features may not work.")
    
    # Create main window
    root = tk.Tk()
    root.title("Tap Ninja Helper")
    root.geometry("800x600")
    
    # Create and run dashboard
    dashboard = Dashboard(root)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()
