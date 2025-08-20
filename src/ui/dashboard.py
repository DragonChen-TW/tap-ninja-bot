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
from PIL import Image, ImageTk

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
            self.root.geometry("900x700")
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
        
        # Variables for image display
        self.last_image = None
        self.last_image_tk = None
        
        # Variables for gold tracking
        self.gold_history = []  # List of (timestamp, gold_value) tuples
        self.last_gold = None
        self.last_gold_time = None
        self.gpm_value = None  # Amortized gold per minute
        self.instant_gpm_value = None  # Instantaneous gold per minute
        self.gph_value = None  # Gold per hour (based on amortized GPM)
        
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
        
        # Last capture timestamp
        self.timestamp_label = ttk.Label(
            control_frame,
            text="Last capture: N/A"
        )
        self.timestamp_label.pack(side=tk.RIGHT, padx=10)
        
        # Main content pane with image and results side by side
        content_pane = ttk.PanedWindow(self.dash_frame, orient=tk.HORIZONTAL)
        content_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image frame (left)
        image_frame = ttk.LabelFrame(content_pane, text="Last Capture")
        content_pane.add(image_frame, weight=1)
        
        # Canvas for displaying the captured image
        self.image_canvas = tk.Canvas(image_frame, bg="black")
        self.image_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message when no image is available
        self.image_canvas.create_text(
            150, 100, 
            text="No capture available", 
            fill="white", 
            font=('Arial', 12)
        )
        
        # Bind resize event to update image on canvas resizing
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Results frame (right)
        results_frame = ttk.LabelFrame(content_pane, text="OCR Results")
        content_pane.add(results_frame, weight=1)
        
        # OCR results text widget
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Metrics frame (bottom)
        metrics_frame = ttk.LabelFrame(self.dash_frame, text="Gold Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Current gold value
        gold_frame = ttk.Frame(metrics_frame)
        gold_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(gold_frame, text="Current Gold:").pack(side=tk.LEFT)
        self.gold_label = ttk.Label(gold_frame, text="N/A")
        self.gold_label.pack(side=tk.LEFT, padx=5)
        
        # Gold per minute
        gpm_frame = ttk.Frame(metrics_frame)
        gpm_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(gpm_frame, text="Gold per minute (amortized):").pack(side=tk.LEFT)
        self.gpm_label = ttk.Label(gpm_frame, text="N/A")
        self.gpm_label.pack(side=tk.LEFT, padx=5)
        
        # Instantaneous gold per minute
        instant_gpm_frame = ttk.Frame(metrics_frame)
        instant_gpm_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(instant_gpm_frame, text="Instant GPM (last capture):").pack(side=tk.LEFT)
        self.instant_gpm_label = ttk.Label(instant_gpm_frame, text="N/A")
        self.instant_gpm_label.pack(side=tk.LEFT, padx=5)
        
        # Gold per hour
        gph_frame = ttk.Frame(metrics_frame)
        gph_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(gph_frame, text="Gold per hour:").pack(side=tk.LEFT)
        self.gph_label = ttk.Label(gph_frame, text="N/A")
        self.gph_label.pack(side=tk.LEFT, padx=5)
        
        # Gold increase since start
        increase_frame = ttk.Frame(metrics_frame)
        increase_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(increase_frame, text="Total increase:").pack(side=tk.LEFT)
        self.increase_label = ttk.Label(increase_frame, text="N/A")
        self.increase_label.pack(side=tk.LEFT, padx=5)
        
        # Time to next upgrade (if specified)
        upgrade_frame = ttk.Frame(metrics_frame)
        upgrade_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(upgrade_frame, text="Time to next upgrade:").pack(side=tk.LEFT)
        self.upgrade_label = ttk.Label(upgrade_frame, text="N/A")
        self.upgrade_label.pack(side=tk.LEFT, padx=5)
        
        # Target upgrade cost input
        target_frame = ttk.Frame(metrics_frame)
        target_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(target_frame, text="Target cost:").pack(side=tk.LEFT)
        self.target_cost_var = tk.StringVar()
        self.target_cost_entry = ttk.Entry(target_frame, textvariable=self.target_cost_var, width=10)
        self.target_cost_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(target_frame, text="Set Target", command=self.set_target_cost).pack(side=tk.LEFT, padx=5)
    
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
            text="Select Window/Area",
            command=self.select_capture_area,
            width=20
        ).grid(row=0, column=2, padx=5)
        
        # Two-step capture option
        two_step_frame = ttk.Frame(capture_frame)
        two_step_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            two_step_frame, 
            text="Capture method:"
        ).grid(row=0, column=0, sticky=tk.W)
        
        # Create radio buttons for capture method
        self.capture_method_var = tk.StringVar(
            value="two_step" if self.config.get("use_two_step_capture", True) else "single"
        )
        
        ttk.Radiobutton(
            two_step_frame,
            text="Two-step (window then sub-area)",
            variable=self.capture_method_var,
            value="two_step",
            command=self.update_capture_method
        ).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Radiobutton(
            two_step_frame,
            text="Single-step (direct area selection)",
            variable=self.capture_method_var,
            value="single",
            command=self.update_capture_method
        ).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Help text for two-step capture
        help_text = (
            "Two-step: First select a window, then an area within it\n"
            "Single-step: Select the capture area directly in one step"
        )
        help_label = ttk.Label(
            two_step_frame, 
            text=help_text,
            foreground="gray",
            font=("Arial", 8)
        )
        help_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
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
        
        # Gold metrics settings
        metrics_frame = ttk.LabelFrame(self.settings_frame, text="Gold Metrics Settings")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # History window for calculations
        history_frame = ttk.Frame(metrics_frame)
        history_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(history_frame, text="Amortization window (minutes):").grid(row=0, column=0, sticky=tk.W)
        
        # Default to 5 minutes or the stored value
        self.history_window_var = tk.StringVar(value=str(self.config.get("gold_history_window", 5.0)))
        history_entry = ttk.Entry(history_frame, textvariable=self.history_window_var, width=5)
        history_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(
            history_frame,
            text="Apply",
            command=self.apply_history_window
        ).grid(row=0, column=2, padx=5)
        
        # Help text for amortized calculations
        help_text = (
            "Longer windows (5-10 minutes) provide more stable GPM calculations\n"
            "Shorter windows (1-2 minutes) respond faster to recent changes"
        )
        help_label = ttk.Label(
            history_frame, 
            text=help_text,
            foreground="gray",
            font=("Arial", 8)
        )
        help_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)
        
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
        # Check if we should use the two-step or single-step selector
        use_two_step = self.config.get("use_two_step_capture", True)
        
        if use_two_step:
            # Use two-step area selector
            from .area_selector import TwoStepAreaSelector
            selector = TwoStepAreaSelector(callback=self.on_two_step_area_selected)
            selector.run()
        else:
            # Use the original area selector
            from .area_selector import AreaSelector
            selector = AreaSelector(callback=self.on_area_selected)
            selector.run()
    
    def on_two_step_area_selected(self, parent_area, sub_area):
        """
        Handle the two-step area selection
        
        Args:
            parent_area: The parent window/screen area
            sub_area: The sub-area for OCR
        """
        if parent_area and sub_area:
            # Update config with both areas
            self.config.set("parent_area", parent_area)
            self.config.set("capture_area", sub_area)
            
            # Update area label - show both the parent and sub-area
            parent_text = f"Parent: ({parent_area['x1']}, {parent_area['y1']}) - ({parent_area['x2']}, {parent_area['y2']})"
            sub_text = f"OCR: ({sub_area['x1']}, {sub_area['y1']}) - ({sub_area['x2']}, {sub_area['y2']})"
            area_text = f"{parent_text} | {sub_text}"
            
            # Update the display with a shortened version
            short_text = f"({sub_area['x1']}, {sub_area['y1']}) - ({sub_area['x2']}, {sub_area['y2']})"
            self.area_label.config(text=short_text)
            
            # Add tooltip with full information
            self.add_tooltip(self.area_label, area_text)
        
        # Restore main window
        self.root.deiconify()
    
    def on_area_selected(self, area):
        """Handle single area selection"""
        if area:
            # Update config - set both parent and capture area to the same
            self.config.set("parent_area", area)
            self.config.set("capture_area", area)
            
            # Update area label
            area_text = f"({area['x1']}, {area['y1']}) - ({area['x2']}, {area['y2']})"
            self.area_label.config(text=area_text)
        
        # Restore main window
        self.root.deiconify()
        
    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget"""
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.attributes("-topmost", True)
        tooltip.overrideredirect(True)
        
        label = tk.Label(
            tooltip,
            text=text,
            background="#FFFFDD",
            relief="solid",
            borderwidth=1,
            padx=5,
            pady=5,
            wraplength=400
        )
        label.pack()
        
        def enter(_):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def leave(_):
            tooltip.withdraw()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
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
    
    def apply_history_window(self):
        """Apply the gold history window setting"""
        try:
            window = float(self.history_window_var.get())
            if window < 0.5:
                messagebox.showwarning("Invalid Window", "Window must be at least 0.5 minutes")
                return
                
            self.config.set("gold_history_window", window)
            messagebox.showinfo("Success", f"Amortization window set to {window} minutes")
            
            # Recalculate metrics with new window
            if self.last_gold is not None:
                # Get current gold and time values
                current_gold = self.last_gold
                current_time = self.last_gold_time
                
                # Calculate amortized GPM with new window
                amortized_increase, time_span, amortized_gpm = self.calculate_gold_increase(window)
                
                if amortized_gpm > 0:
                    # Update display with new amortized value
                    self.update_gpm(amortized_gpm, current_gold)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def update_capture_method(self):
        """Update the capture method setting"""
        use_two_step = self.capture_method_var.get() == "two_step"
        self.config.set("use_two_step_capture", use_two_step)
    
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
            # Get capture areas
            use_two_step = self.config.get("use_two_step_capture", True)
            
            if use_two_step:
                # For two-step capture, we need both the parent and sub areas
                parent_area = self.config.get("parent_area")
                ocr_area = self.config.get("capture_area")
                
                # First capture the parent area
                parent_screenshot = self.screen_capture.capture_area(
                    parent_area["x1"], parent_area["y1"], 
                    parent_area["x2"], parent_area["y2"]
                )
                
                # Calculate the sub-area coordinates relative to the parent screenshot
                sub_x1 = ocr_area["x1"] - parent_area["x1"]
                sub_y1 = ocr_area["y1"] - parent_area["y1"]
                sub_x2 = ocr_area["x2"] - parent_area["x1"]
                sub_y2 = ocr_area["y2"] - parent_area["y1"]
                
                # Ensure coordinates are within bounds
                sub_x1 = max(0, sub_x1)
                sub_y1 = max(0, sub_y1)
                sub_x2 = min(parent_screenshot.width, sub_x2)
                sub_y2 = min(parent_screenshot.height, sub_y2)
                
                # Crop the sub-area for OCR
                screenshot = parent_screenshot.crop((sub_x1, sub_y1, sub_x2, sub_y2))
            else:
                # For single-step capture, just get the capture area directly
                area = self.config.get("capture_area")
                
                # Take screenshot directly of the OCR area
                screenshot = self.screen_capture.capture_area(
                    area["x1"], area["y1"], area["x2"], area["y2"]
                )
            
            # Run OCR
            text = self.text_recognition.extract_text(screenshot)
            numbers = self.text_recognition.extract_numbers(screenshot)
            
            # Show result with image and current timestamp
            current_time = time.time()
            self.update_results(text, numbers, screenshot, current_time)
            
            # Process gold value for metrics if numbers were found
            if numbers and len(numbers) > 0:
                gold_value = numbers[0]  # Assume first number is gold
                
                # Add to gold history
                self._add_gold_history(current_time, gold_value)
                
                # If we have previous values, calculate instantaneous GPM
                if self.last_gold is not None and self.last_gold_time is not None and current_time > self.last_gold_time:
                    time_diff_minutes = (current_time - self.last_gold_time) / 60.0
                    gold_diff = gold_value - self.last_gold
                    instant_gpm = gold_diff / time_diff_minutes if time_diff_minutes > 0 else 0
                    
                    # Update metrics with both instantaneous and amortized values
                    self.update_gpm(instant_gpm, gold_value)
                else:
                    # First capture, just update the current gold display
                    self.gold_label.config(text=f"{gold_value:,.2f}")
                    self.instant_gpm_label.config(text="N/A")
            
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
                    # Get capture areas
                    use_two_step = self.config.get("use_two_step_capture", True)
                    
                    if use_two_step:
                        # For two-step capture, we need both the parent and sub areas
                        parent_area = self.config.get("parent_area")
                        ocr_area = self.config.get("capture_area")
                        
                        # First capture the parent area
                        parent_screenshot = thread_screen_capture.capture_area(
                            parent_area["x1"], parent_area["y1"], 
                            parent_area["x2"], parent_area["y2"]
                        )
                        
                        # Calculate the sub-area coordinates relative to the parent screenshot
                        sub_x1 = ocr_area["x1"] - parent_area["x1"]
                        sub_y1 = ocr_area["y1"] - parent_area["y1"]
                        sub_x2 = ocr_area["x2"] - parent_area["x1"]
                        sub_y2 = ocr_area["y2"] - parent_area["y1"]
                        
                        # Ensure coordinates are within bounds
                        sub_x1 = max(0, sub_x1)
                        sub_y1 = max(0, sub_y1)
                        sub_x2 = min(parent_screenshot.width, sub_x2)
                        sub_y2 = min(parent_screenshot.height, sub_y2)
                        
                        # Crop the sub-area for OCR
                        screenshot = parent_screenshot.crop((sub_x1, sub_y1, sub_x2, sub_y2))
                    else:
                        # For single-step capture, just get the capture area directly
                        area = self.config.get("capture_area")
                        
                        # Take screenshot directly of the OCR area
                        screenshot = thread_screen_capture.capture_area(
                            area["x1"], area["y1"], area["x2"], area["y2"]
                        )
                    
                    # Run OCR on the appropriate screenshot
                    text = self.text_recognition.extract_text(screenshot)
                    numbers = self.text_recognition.extract_numbers(screenshot)
                    
                    # Get current timestamp
                    current_time = time.time()
                    
                    # Update UI from main thread
                    self.root.after(0, self.update_results, text, numbers, screenshot, current_time)
                    
                    # Calculate GPM if numbers found
                    if numbers and len(numbers) > 0:
                        current_time = time.time()
                        gold = numbers[0]  # Assume first number is gold
                        
                        # Add to gold history (in main thread to avoid threading issues)
                        self.root.after(0, self._add_gold_history, current_time, gold)
                        
                        if last_gold is not None and current_time > last_time:
                            # Calculate instantaneous GPM (for debugging and comparison)
                            time_diff = (current_time - last_time) / 60.0  # Convert to minutes
                            gold_diff = gold - last_gold
                            instant_gpm = gold_diff / time_diff
                            
                            # Update metrics from main thread using the amortized calculation
                            self.root.after(0, self.update_gpm, instant_gpm, gold)
                        else:
                            # First capture or time issue, just update the gold display
                            self.root.after(0, lambda: self.gold_label.config(text=f"{gold:,.2f}"))
                        
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
    
    def update_results(self, text, numbers, screenshot=None, timestamp=None):
        """
        Update the results text and image display (called from main thread)
        
        Args:
            text: OCR text result
            numbers: Extracted numbers
            screenshot: The captured screenshot image (PIL Image)
            timestamp: Timestamp of the capture
        """
        # Update the OCR text results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"OCR Text:\n{text}\n\nNumbers:\n{numbers}")
        
        # Update the image display if provided
        if screenshot:
            self.display_image(screenshot)
            self.last_image = screenshot
            
        # Update the timestamp if provided
        if timestamp:
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            self.timestamp_label.config(text=f"Last capture: {formatted_time}")
            
    def display_image(self, img):
        """
        Display an image on the canvas
        
        Args:
            img: PIL Image to display
        """
        # Get canvas dimensions
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        # If canvas hasn't been drawn yet, use reasonable defaults
        if canvas_width <= 1:
            canvas_width = 300
        if canvas_height <= 1:
            canvas_height = 200
            
        # Resize the image to fit the canvas while maintaining aspect ratio
        img_width, img_height = img.size
        scale = min(canvas_width/img_width, canvas_height/img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to Tkinter PhotoImage
        from PIL import ImageTk
        self.last_image_tk = ImageTk.PhotoImage(resized_img)
        
        # Clear canvas and display the new image
        self.image_canvas.delete("all")
        x_position = (canvas_width - new_width) // 2
        y_position = (canvas_height - new_height) // 2
        self.image_canvas.create_image(x_position, y_position, anchor=tk.NW, image=self.last_image_tk)
    
    def update_gpm(self, instant_gpm, gold_value):
        """
        Update the gold metrics labels (called from main thread)
        
        Args:
            instant_gpm: Instantaneous gold per minute (from last two measurements)
            gold_value: Current gold value
        """
        # Calculate amortized GPM over a window (default 5 minutes)
        window_minutes = self.config.get("gold_history_window", 5.0)  # 5 minutes default
        amortized_increase, time_span, amortized_gpm = self.calculate_gold_increase(window_minutes)
        
        # If we don't have enough history, fall back to instantaneous value
        if amortized_gpm > 0:
            self.gpm_value = amortized_gpm
        else:
            self.gpm_value = instant_gpm
            
        self.gph_value = self.gpm_value * 60  # Convert to gold per hour
        
        # Update the current gold value
        self.gold_label.config(text=f"{gold_value:,.2f}")
        
        # Update both GPM displays
        self.gpm_label.config(text=f"{self.gpm_value:,.2f}")
        self.instant_gpm_label.config(text=f"{instant_gpm:,.2f}")
        
        # Update GPH display
        self.gph_label.config(text=f"{self.gph_value:,.2f}")
        
        # Show the window used for amortization as tooltip
        window_text = f"Using {window_minutes} minute window for amortized calculation"
        self.add_tooltip(self.gpm_label, window_text)
        
        # Calculate total increase if we have history
        if len(self.gold_history) >= 2:
            first_gold = self.gold_history[0][1]
            total_increase = gold_value - first_gold
            self.increase_label.config(text=f"{total_increase:,.2f}")
            
            # Add more detailed tooltip
            start_time = time.strftime("%H:%M:%S", time.localtime(self.gold_history[0][0]))
            end_time = time.strftime("%H:%M:%S", time.localtime(self.gold_history[-1][0]))
            time_diff_minutes = (self.gold_history[-1][0] - self.gold_history[0][0]) / 60
            tooltip_text = f"Total increase: {total_increase:,.2f} gold over {time_diff_minutes:.1f} minutes\n"
            tooltip_text += f"From {start_time} to {end_time}"
            self.add_tooltip(self.increase_label, tooltip_text)
        
        # Update time to upgrade if we have a target
        self.update_upgrade_time()
    
    def set_target_cost(self):
        """Set the target upgrade cost from the entry field"""
        try:
            # Get the target cost from the entry
            cost_text = self.target_cost_var.get()
            
            # Remove commas if present
            cost_text = cost_text.replace(',', '')
            
            # Convert to float
            target_cost = float(cost_text)
            
            # Store in config
            self.config.set("target_upgrade_cost", target_cost)
            
            # Update the upgrade time estimate
            self.update_upgrade_time()
            
            # Clear the entry
            self.target_cost_var.set("")
            
        except ValueError:
            messagebox.showerror("Invalid Cost", "Please enter a valid number for the target cost.")
    
    def _add_gold_history(self, timestamp, gold_value):
        """
        Add a gold value to history (must be called from main thread)
        
        Args:
            timestamp: Time when the gold value was captured
            gold_value: The gold value
        """
        # Add to history
        self.gold_history.append((timestamp, gold_value))
        
        # Keep only the last 100 entries to avoid memory issues
        if len(self.gold_history) > 100:
            self.gold_history.pop(0)
            
        # Update last gold value and time
        self.last_gold = gold_value
        self.last_gold_time = timestamp
    
    def calculate_gold_increase(self, time_period_minutes=None):
        """
        Calculate gold increase over a specific time period
        
        Args:
            time_period_minutes: Time period in minutes to look back, or None for all history
            
        Returns:
            Tuple of (gold_increase, time_diff_minutes, gpm)
        """
        if not self.gold_history or len(self.gold_history) < 2:
            return (0, 0, 0)
            
        now = time.time()
        
        if time_period_minutes is None:
            # Use all history
            start_time, start_gold = self.gold_history[0]
        else:
            # Find the closest entry to the requested time period
            target_time = now - (time_period_minutes * 60)
            
            # Default to the oldest entry
            start_time, start_gold = self.gold_history[0]
            
            # If we don't have enough history yet, just use what we have
            if self.gold_history[0][0] > target_time:
                start_time, start_gold = self.gold_history[0]
            else:
                # Find the entry closest to but not before target_time
                closest_idx = 0
                for i, (t, g) in enumerate(self.gold_history):
                    if t <= target_time:
                        closest_idx = i
                    else:
                        break
                        
                start_time, start_gold = self.gold_history[closest_idx]
        
        # Get the most recent entry
        end_time, end_gold = self.gold_history[-1]
        
        # Calculate time difference in minutes
        time_diff_minutes = (end_time - start_time) / 60
        
        # Calculate gold difference
        gold_increase = end_gold - start_gold
        
        # Calculate gold per minute with safety check
        if time_diff_minutes > 0:
            gpm = gold_increase / time_diff_minutes
        else:
            gpm = 0
        
        return (gold_increase, time_diff_minutes, gpm)
    
    def update_upgrade_time(self):
        """Update the time to upgrade estimate based on current GPM"""
        # Check if we have a GPM value and a target cost
        if self.gpm_value is None:
            return
        
        target_cost = self.config.get("target_upgrade_cost", None)
        if target_cost is None:
            self.upgrade_label.config(text="Set a target cost")
            return
            
        # Get current gold from the latest history entry
        if not self.gold_history:
            self.upgrade_label.config(text="Waiting for data...")
            return
            
        current_gold = self.gold_history[-1][1]
        
        # Calculate how much more gold is needed
        needed_gold = max(0, target_cost - current_gold)
        
        # Calculate time in minutes
        if self.gpm_value > 0:
            minutes_needed = needed_gold / self.gpm_value
            
            # Format time nicely
            if minutes_needed < 1:
                seconds = int(minutes_needed * 60)
                time_text = f"{seconds} seconds"
            elif minutes_needed < 60:
                time_text = f"{int(minutes_needed)} minutes"
            else:
                hours = int(minutes_needed / 60)
                mins = int(minutes_needed % 60)
                time_text = f"{hours} hours, {mins} minutes"
                
            self.upgrade_label.config(text=time_text)
        else:
            self.upgrade_label.config(text="N/A")
    
    def on_canvas_resize(self, event=None):
        """Handle canvas resize event to adjust displayed image"""
        if self.last_image:
            # Redisplay the image with new canvas dimensions
            self.display_image(self.last_image)
    
    def run(self):
        """Run the dashboard UI"""
        if self.owns_root:
            self.root.mainloop()
