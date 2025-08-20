"""
Main dashboard UI module for Tap Ninja Helper.
Displays the main application interface with OCR results and controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from typing import Dict, Any, Optional, List
import os

from ..config import Config
from ..capture.screenshot import ScreenCapture
from ..ocr.text_recognition import TextRecognition
from .area_selector import AreaSelector

class Dashboard:
    """Main application dashboard UI class"""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        Initialize the dashboard UI.
        
        Args:
            root: Tkinter root window. If None, creates a new one.
        """
        # Create a new root window if none provided
        if root is None:
            self.root = tk.Tk()
            self.root.title("Tap Ninja Helper")
            self.root.geometry("800x600")
            self.owns_root = True
        else:
            self.root = root
            self.owns_root = False
        
        # Load configuration
        self.config = Config()
        
        # Initialize components
        self.screen_capture = ScreenCapture()
        self.text_recognition = TextRecognition(self.config.get_tesseract_path())
        
        # Variables for capture thread
        self.capture_thread = None
        self.capture_running = False
        self.capture_interval = self.config.get("capture_interval", 5)
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        # Create a notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.dash_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dash_frame, text="Dashboard")
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Set up dashboard tab
        self.setup_dashboard_tab()
        
        # Set up settings tab
        self.setup_settings_tab()
    
    def setup_dashboard_tab(self):
        """Set up the dashboard tab"""
        # Control frame (top)
        control_frame = ttk.Frame(self.dash_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start/Stop button
        self.capture_btn = ttk.Button(
            control_frame,
            text="Start Capture",
            command=self.toggle_capture
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="Status: Not running"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Results frame (middle)
        results_frame = ttk.LabelFrame(self.dash_frame, text="OCR Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # OCR results text widget
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Metrics frame (bottom)
        metrics_frame = ttk.LabelFrame(self.dash_frame, text="Game Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Gold per minute
        gpm_frame = ttk.Frame(metrics_frame)
        gpm_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(gpm_frame, text="Gold per minute:").pack(side=tk.LEFT)
        self.gpm_label = ttk.Label(gpm_frame, text="N/A")
        self.gpm_label.pack(side=tk.LEFT, padx=5)
        
        # Time to next upgrade
        upgrade_frame = ttk.Frame(metrics_frame)
        upgrade_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(upgrade_frame, text="Time to next upgrade:").pack(side=tk.LEFT)
        self.upgrade_label = ttk.Label(upgrade_frame, text="N/A")
        self.upgrade_label.pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self):
        """Set up the settings tab"""
        # Capture settings
        capture_frame = ttk.LabelFrame(self.settings_frame, text="Capture Settings")
        capture_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Capture area
        area_frame = ttk.Frame(capture_frame)
        area_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(area_frame, text="Capture area:").grid(row=0, column=0, sticky=tk.W)
        
        # Show current capture area
        capture_area = self.config.get("capture_area")
        area_text = f"({capture_area['x1']}, {capture_area['y1']}) - ({capture_area['x2']}, {capture_area['y2']})"
        self.area_label = ttk.Label(area_frame, text=area_text)
        self.area_label.grid(row=0, column=1, padx=5)
        
        # Button to select capture area
        ttk.Button(
            area_frame,
            text="Select Area",
            command=self.select_capture_area
        ).grid(row=0, column=2, padx=5)
        
        # Capture interval
        interval_frame = ttk.Frame(capture_frame)
        interval_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(interval_frame, text="Capture interval (seconds):").grid(row=0, column=0, sticky=tk.W)
        
        self.interval_var = tk.StringVar(value=str(self.capture_interval))
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=5)
        interval_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(
            interval_frame,
            text="Apply",
            command=self.apply_interval
        ).grid(row=0, column=2, padx=5)
        
        # OCR settings
        ocr_frame = ttk.LabelFrame(self.settings_frame, text="OCR Settings")
        ocr_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tesseract path
        tesseract_frame = ttk.Frame(ocr_frame)
        tesseract_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(tesseract_frame, text="Tesseract path:").grid(row=0, column=0, sticky=tk.W)
        
        self.tesseract_var = tk.StringVar(value=self.config.get_tesseract_path())
        tesseract_entry = ttk.Entry(tesseract_frame, textvariable=self.tesseract_var, width=50)
        tesseract_entry.grid(row=0, column=1, padx=5, sticky=tk.W+tk.E)
        
        ttk.Button(
            tesseract_frame,
            text="Apply",
            command=self.apply_tesseract_path
        ).grid(row=0, column=2, padx=5)
        
        # Save and load settings
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Test OCR",
            command=self.test_ocr
        ).pack(side=tk.LEFT, padx=5)
    
    def select_capture_area(self):
        """Open the area selector to choose a capture area"""
        # Minimize the main window
        self.root.iconify()
        
        # Wait a bit for window to minimize
        self.root.after(500, self.show_area_selector)
    
    def show_area_selector(self):
        """Show the area selector window"""
        selector = AreaSelector(callback=self.on_area_selected)
        selector.run()
    
    def on_area_selected(self, area):
        """Handle area selection"""
        if area:
            # Update config
            self.config.set("capture_area", area)
            
            # Update area label
            area_text = f"({area['x1']}, {area['y1']}) - ({area['x2']}, {area['y2']})"
            self.area_label.config(text=area_text)
        
        # Restore main window
        self.root.deiconify()
    
    def apply_interval(self):
        """Apply the capture interval setting"""
        try:
            interval = float(self.interval_var.get())
            if interval < 0.1:
                messagebox.showwarning("Invalid Interval", "Interval must be at least 0.1 seconds")
                return
                
            self.capture_interval = interval
            self.config.set("capture_interval", interval)
            messagebox.showinfo("Success", f"Capture interval set to {interval} seconds")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def apply_tesseract_path(self):
        """Apply the Tesseract path setting"""
        path = self.tesseract_var.get()
        
        if not os.path.exists(path):
            messagebox.showwarning("Invalid Path", f"The file does not exist: {path}")
            return
            
        self.config.set("tesseract_path", path)
        self.text_recognition = TextRecognition(path)
        messagebox.showinfo("Success", "Tesseract path updated")
    
    def save_settings(self):
        """Save all settings to config file"""
        self.config.save()
        messagebox.showinfo("Success", "Settings saved")
    
    def test_ocr(self):
        """Test OCR on the current capture area"""
        try:
            # Get capture area
            area = self.config.get("capture_area")
            
            # Take screenshot
            screenshot = self.screen_capture.capture_area(
                area["x1"], area["y1"], area["x2"], area["y2"]
            )
            
            # Run OCR
            text = self.text_recognition.extract_text(screenshot)
            
            # Show result
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"OCR Test Result:\n{text}")
            
        except Exception as e:
            messagebox.showerror("OCR Test Error", f"Error: {str(e)}")
    
    def toggle_capture(self):
        """Start or stop the capture process"""
        if self.capture_running:
            # Stop capture
            self.capture_running = False
            if self.capture_thread:
                self.capture_thread.join(timeout=1.0)
            
            self.capture_btn.config(text="Start Capture")
            self.status_label.config(text="Status: Not running")
        else:
            # Start capture
            self.capture_running = True
            self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
            self.capture_thread.start()
            
            self.capture_btn.config(text="Stop Capture")
            self.status_label.config(text="Status: Running")
    
    def capture_loop(self):
        """Main capture loop (runs in a separate thread)"""
        # Variables for GPM calculation
        last_gold = None
        last_time = time.time()
        
        # Create a separate ScreenCapture instance for this thread
        from ..capture.screenshot import ScreenCapture
        thread_screen_capture = ScreenCapture(use_mss=True)
        
        try:
            while self.capture_running:
                try:
                    # Get capture area
                    area = self.config.get("capture_area")
                    
                    # Take screenshot using thread's own capture instance
                    screenshot = thread_screen_capture.capture_area(
                        area["x1"], area["y1"], area["x2"], area["y2"]
                    )
                    
                    # Run OCR
                    text = self.text_recognition.extract_text(screenshot)
                    numbers = self.text_recognition.extract_numbers(screenshot)
                    
                    # Update UI from main thread
                    self.root.after(0, self.update_results, text, numbers)
                    
                    # Calculate GPM if numbers found
                    if numbers and len(numbers) > 0:
                        current_time = time.time()
                        gold = numbers[0]  # Assume first number is gold
                        
                        if last_gold is not None and current_time > last_time:
                            time_diff = (current_time - last_time) / 60.0  # Convert to minutes
                            gold_diff = gold - last_gold
                            gpm = gold_diff / time_diff
                            
                            # Update GPM label from main thread
                            self.root.after(0, self.update_gpm, gpm)
                        
                        # Update last values
                        last_gold = gold
                        last_time = current_time
                    
                except Exception as e:
                    # Log error but keep running
                    print(f"Error in capture loop: {str(e)}")
                
                # Wait for next capture
                time.sleep(self.capture_interval)
        finally:
            # Clean up resources when thread exits
            try:
                thread_screen_capture.close()
            except:
                pass
    
    def update_results(self, text, numbers):
        """Update the results text (called from main thread)"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"OCR Text:\n{text}\n\nNumbers:\n{numbers}")
    
    def update_gpm(self, gpm):
        """Update the GPM label (called from main thread)"""
        self.gpm_label.config(text=f"{gpm:.2f}")
        
        # TODO: Update time to upgrade based on GPM
        # This would require tracking the target upgrade cost
    
    def run(self):
        """Run the dashboard UI"""
        if self.owns_root:
            self.root.mainloop()
