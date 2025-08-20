# Tech Stack: Tap Ninja Helper

### 1. Programming Language
*   **Python:** A versatile and widely-supported language with excellent libraries for this project.

### 2. Screen Capture & Automation
*   **PyAutoGUI:** Used for taking screenshots of the game window. It can also be used for mouse and keyboard automation if needed in the future.

### 3. Image Processing
*   **Pillow (PIL Fork):** A dependency of PyAutoGUI, this library will be used for basic image manipulation, such as cropping the screenshots to isolate specific data points (e.g., the gold count) before OCR analysis.

### 4. Optical Character Recognition (OCR)
*   **Tesseract OCR Engine:** A powerful and accurate open-source OCR engine maintained by Google. It will need to be installed on the system separately.
*   **Pytesseract:** A Python wrapper library that allows your script to easily use the Tesseract engine to extract numbers from the processed images.

### 5. Graphical User Interface (GUI)
*   **Tkinter:** Python's standard built-in GUI library. It is simple to use and sufficient for creating the application's dashboard to display the captured data and calculations.