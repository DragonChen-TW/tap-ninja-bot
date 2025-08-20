"""
Screenshot test script for Tap Ninja Helper.
This script tests the screenshot capabilities and saves sample screenshots.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture.screenshot import ScreenCapture
from src.ui.area_selector import AreaSelector
from src.config import Config


class ScreenshotTest:
    """Test application for screenshot functionality"""
    
    def __init__(self):
        """Initialize the test application"""
        self.root = tk.Tk()
        self.root.title("Screenshot Test")
        self.root.geometry("800x600")
        
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Set up UI
        self.setup_ui()
        
        # Initialize screenshot capture with both methods
        self.mss_capture = ScreenCapture(use_mss=True)
        self.pyautogui_capture = ScreenCapture(use_mss=False)
        
        # Selected area
        self.selected_area = {"x1": 0, "y1": 0, "x2": 300, "y2": 300}  # Default
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Area selection
        area_frame = ttk.LabelFrame(main_frame, text="Screenshot Area", padding="10")
        area_frame.pack(fill=tk.X, pady=10)
        
        # Show current area
        self.area_label = ttk.Label(
            area_frame,
            text=f"Selected Area: (0, 0) - (300, 300)"
        )
        self.area_label.pack(pady=5)
        
        # Select area button
        select_btn = ttk.Button(
            area_frame,
            text="Select Area",
            command=self.select_area
        )
        select_btn.pack(pady=5)
        
        # Screenshot method frame
        method_frame = ttk.LabelFrame(main_frame, text="Screenshot Method", padding="10")
        method_frame.pack(fill=tk.X, pady=10)
        
        # Method selection
        self.method_var = tk.StringVar(value="mss")
        
        mss_radio = ttk.Radiobutton(
            method_frame,
            text="MSS (faster)",
            variable=self.method_var,
            value="mss"
        )
        mss_radio.pack(anchor=tk.W, pady=2)
        
        pyautogui_radio = ttk.Radiobutton(
            method_frame,
            text="PyAutoGUI",
            variable=self.method_var,
            value="pyautogui"
        )
        pyautogui_radio.pack(anchor=tk.W, pady=2)
        
        # Screenshot button
        take_screenshot_btn = ttk.Button(
            main_frame,
            text="Take Screenshot",
            command=self.take_screenshot
        )
        take_screenshot_btn.pack(pady=10)
        
        # Multiple screenshots frame
        multi_frame = ttk.LabelFrame(main_frame, text="Multiple Screenshots", padding="10")
        multi_frame.pack(fill=tk.X, pady=10)
        
        # Count entry
        count_frame = ttk.Frame(multi_frame)
        count_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(count_frame, text="Number of screenshots:").pack(side=tk.LEFT)
        
        self.count_var = tk.StringVar(value="5")
        count_entry = ttk.Entry(count_frame, textvariable=self.count_var, width=5)
        count_entry.pack(side=tk.LEFT, padx=5)
        
        # Interval entry
        interval_frame = ttk.Frame(multi_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(interval_frame, text="Interval (seconds):").pack(side=tk.LEFT)
        
        self.interval_var = tk.StringVar(value="1.0")
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=5)
        interval_entry.pack(side=tk.LEFT, padx=5)
        
        # Multiple screenshots button
        multi_btn = ttk.Button(
            multi_frame,
            text="Take Multiple Screenshots",
            command=self.take_multiple_screenshots
        )
        multi_btn.pack(pady=5)
        
        # Result frame
        result_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Result text
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(self.result_text, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def select_area(self):
        """Open the area selector to choose a screenshot area"""
        # Minimize the main window
        self.root.iconify()
        
        # Wait a bit for window to minimize
        self.root.after(500, self._show_area_selector)
    
    def _show_area_selector(self):
        """Show the area selector window"""
        selector = AreaSelector(callback=self.on_area_selected)
        selector.run()
    
    def on_area_selected(self, area):
        """Handle area selection"""
        if area:
            self.selected_area = area
            area_text = f"Selected Area: ({area['x1']}, {area['y1']}) - ({area['x2']}, {area['y2']})"
            self.area_label.config(text=area_text)
        
        # Restore main window
        self.root.deiconify()
    
    def take_screenshot(self):
        """Take a single screenshot of the selected area"""
        try:
            self.status_var.set("Taking screenshot...")
            self.root.update_idletasks()
            
            # Choose capture method
            use_mss = self.method_var.get() == "mss"
            capture = self.mss_capture if use_mss else self.pyautogui_capture
            
            # Take screenshot
            screenshot = capture.capture_area(
                self.selected_area["x1"],
                self.selected_area["y1"],
                self.selected_area["x2"],
                self.selected_area["y2"]
            )
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            method_name = "mss" if use_mss else "pyautogui"
            filename = f"screenshot_{method_name}_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Save screenshot
            screenshot.save(filepath)
            
            # Log result
            self.log_result(f"Screenshot saved to: {filepath}")
            
            # Open the screenshot
            self.status_var.set(f"Screenshot saved to {filename}")
            
        except Exception as e:
            self.status_var.set("Error taking screenshot")
            self.log_result(f"ERROR: {str(e)}")
    
    def take_multiple_screenshots(self):
        """Take multiple screenshots with a specified interval"""
        try:
            # Parse inputs
            count = int(self.count_var.get())
            interval = float(self.interval_var.get())
            
            if count <= 0 or interval <= 0:
                raise ValueError("Count and interval must be positive numbers")
            
            self.log_result(f"Taking {count} screenshots with {interval}s interval...")
            
            # Choose capture method
            use_mss = self.method_var.get() == "mss"
            capture = self.mss_capture if use_mss else self.pyautogui_capture
            method_name = "mss" if use_mss else "pyautogui"
            
            # Take screenshots
            for i in range(count):
                # Update status
                self.status_var.set(f"Taking screenshot {i+1}/{count}...")
                self.root.update_idletasks()
                
                # Take screenshot
                screenshot = capture.capture_area(
                    self.selected_area["x1"],
                    self.selected_area["y1"],
                    self.selected_area["x2"],
                    self.selected_area["y2"]
                )
                
                # Generate filename with timestamp and index
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{method_name}_{timestamp}_{i+1}.png"
                filepath = os.path.join(self.screenshots_dir, filename)
                
                # Save screenshot
                screenshot.save(filepath)
                
                # Log result
                self.log_result(f"Screenshot {i+1}/{count} saved to: {filename}")
                
                # Wait for next screenshot, except for the last one
                if i < count - 1:
                    time.sleep(interval)
            
            self.status_var.set(f"Completed {count} screenshots")
            
        except ValueError as e:
            self.status_var.set("Invalid input values")
            self.log_result(f"ERROR: {str(e)}")
        except Exception as e:
            self.status_var.set("Error taking screenshots")
            self.log_result(f"ERROR: {str(e)}")
    
    def log_result(self, message):
        """Log a message to the result text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.result_text.see(tk.END)  # Scroll to bottom
    
    def run(self):
        """Run the test application"""
        self.root.mainloop()
        
        # Clean up
        self.mss_capture.close()


def main():
    """Main entry point"""
    app = ScreenshotTest()
    app.run()


if __name__ == "__main__":
    main()
