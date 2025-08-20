# Implementation Plan: Tap Ninja Helper (WSL Ubuntu Environment)

This plan provides step-by-step instructions for implementing the Tap Ninja Helper application in a WSL Ubuntu environment. Each step includes clear, actionable instructions with technology integration details specific to WSL.

---

## 1. Set Up Project Structure and WSL Environment
- **Instruction:** Create the initial Python project directory with subfolders for source code, assets, and documentation.
- **Tech Integration:** 
  - Set up a virtual environment using uv package manager
  - Install system dependencies required for WSL: `sudo apt install python3-tk tesseract-ocr`
  - Configure X11 display server connection for GUI applications
  - Install the initial Python dependencies from requirements.txt

## 2. Initialize Version Control
- **Instruction:** Initialize a Git repository and add a .gitignore file for Python.
- **Tech Integration:** Configure .gitignore to exclude virtual environment folders, cache files, and other Python-specific items.

## 3. Set Up Basic Application Framework
- **Instruction:** Create a main entry point with a basic application loop using Tkinter.
- **Tech Integration:** 
  - Import Tkinter for the GUI framework (using Python3-tk installed via apt)
  - Create a main application window
  - Set up a basic event loop
  - Ensure proper X11 display configuration for WSL
- **Validation:** Run the application with X server running on Windows; confirm that the window opens and closes properly.

## 4. Implement User Settings Storage
- **Instruction:** Create a mechanism to store and retrieve user settings between sessions.
- **Tech Integration:** 
  - Use JSON or SQLite for settings storage
  - Include settings for capture area coordinates, update frequency, etc.
- **Validation:** Verify settings persist when the application is closed and reopened.

## 5. Implement Screenshot Capture
- **Instruction:** Add functionality to capture screenshots from a specified area of the screen.
- **Tech Integration:** 
  - Use MSS library for fast and efficient screenshot capture in WSL
  - Ensure proper X11 access for screen capture in WSL environment
  - Allow capturing a specific area of the screen every 5 seconds
  - Implement a preview of the capture area
- **Validation:** Verify the application can capture the specified screen area correctly through X server.

## 6. Implement OCR Processing
- **Instruction:** Add OCR functionality to extract numbers and characters from screenshot areas.
- **Tech Integration:** 
  - Use Tesseract OCR engine installed via apt (`sudo apt install tesseract-ocr tesseract-ocr-eng`)
  - Use Pytesseract Python wrapper with explicit path to Tesseract executable
  - Focus on detecting one line of numbers and characters from a small area
  - Use Pillow (PIL) and OpenCV (headless version) for pre-processing images before OCR
- **Validation:** Test OCR accuracy with sample screenshots containing typical game numbers.

## 7. Create Area Selection UI
- **Instruction:** Implement UI for users to select the capture area and areas for OCR processing.
- **Tech Integration:** 
  - Use Tkinter Canvas for drawing selection rectangles
  - Store coordinates in user settings
- **Validation:** Verify users can select and save areas for monitoring.

## 8. Implement Basic Calculations
- **Instruction:** Add logic to process OCR data and perform simple calculations.
- **Tech Integration:**
  - Parse OCR output to extract numerical values
  - Calculate rates and estimations based on time differences
- **Validation:** Verify calculations based on sample data.

## 9. Build Main Application Dashboard
- **Instruction:** Create the primary UI that displays captured data and calculations.
- **Tech Integration:**
  - Use Tkinter frames, labels, and other widgets to create a clean interface
  - Implement real-time updates of the dashboard
- **Validation:** Verify the dashboard properly displays and updates all relevant information.

## 10. Implement Error Handling and Logging
- **Instruction:** Add robust error handling for common failure scenarios.
- **Tech Integration:**
  - Use Python's logging module with Rich for better console output
  - Handle OCR failures, screenshot errors, and calculation issues
  - Handle WSL-specific errors like X server connection failures
  - Provide user feedback for errors
- **Validation:** Test error scenarios to ensure the application handles them gracefully.

## 11. WSL-Specific Testing
- **Instruction:** Create a test script to verify WSL environment configuration.
- **Tech Integration:**
  - Test X server connection
  - Verify screenshot capabilities in WSL
  - Confirm Tesseract OCR works correctly
  - Check all dependencies are properly installed
- **Validation:** Run the test script and verify all components are working correctly.

---

**End of Tap Ninja Helper Implementation Plan**

*Note: No unit tests are required for this implementation plan. The application should be validated through manual testing of each component.*

*WSL Environment Notes:*
1. *Always ensure X server is running on Windows before starting the application*
2. *If screenshot functionality fails, try using alternative methods (MSS or pyscreenshot)*
3. *For Tesseract issues, verify the path is correctly configured in the code*
