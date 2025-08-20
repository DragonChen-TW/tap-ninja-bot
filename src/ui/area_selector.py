"""
Area selection UI module for Tap Ninja Helper.
Allows users to select screen areas for capture and OCR, or select a specific window.
"""

import tkinter as tk
from tkinter import ttk, simpledialog
from typing import Dict, Any, Optional, Callable, Tuple, List

# Import pygetwindow for window selection
try:
    import pygetwindow as gw
    HAS_WINDOW_SUPPORT = True
except ImportError:
    print("pygetwindow not found. Window selection feature will be disabled.")
    HAS_WINDOW_SUPPORT = False

class TwoStepAreaSelector:
    """Main class to handle the two-step area selection process"""
    
    def __init__(self, callback: Optional[Callable[[Dict[str, int], Dict[str, int]], None]] = None):
        """
        Initialize the two-step area selector.
        
        Args:
            callback: Function to call with selected areas (parent_area, sub_area)
        """
        self.callback = callback
        self.parent_area = None
        self.root = tk.Tk()
        self.root.title("Two-Step Area Selection")
        self.root.geometry("450x250")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI for the two-step selector"""
        frame = ttk.Frame(self.root, padding="10 10 10 10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            frame, 
            text="Two-Step Capture Area Selection", 
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))
        
        # Instructions
        ttk.Label(
            frame,
            text="Step 1: First select a window or full-screen area\n"
                 "Step 2: Then select a specific region inside that area for OCR",
            wraplength=400,
            justify=tk.LEFT
        ).pack(pady=(0, 15))
        
        # Select window button
        self.window_btn = ttk.Button(
            frame,
            text="Step 1: Select Window",
            command=self.select_window_first,
            width=30
        )
        self.window_btn.pack(pady=5)
        
        # Full screen button
        ttk.Button(
            frame,
            text="Step 1: Use Full Screen",
            command=self.select_full_screen_first,
            width=30
        ).pack(pady=5)
        
        # Manual selection button
        ttk.Button(
            frame,
            text="Step 1: Draw Custom Screen Area",
            command=self.select_manual_area_first,
            width=30
        ).pack(pady=5)
        
        # Disable window selection if not supported
        if not HAS_WINDOW_SUPPORT:
            self.window_btn.config(state=tk.DISABLED)
            ttk.Label(
                frame,
                text="Window selection requires pygetwindow package",
                foreground="red"
            ).pack(pady=5)
    
    def select_window_first(self):
        """Select a window as the first step"""
        # Hide main window
        self.root.withdraw()
        
        # Release any grab to prevent UI issues
        try:
            self.root.grab_release()
        except Exception:
            pass
            
        # Create window selector after a slight delay to ensure window management operations complete
        self.root.after(100, lambda: WindowSelector(self.root, "Step 1: Select Window", self.on_parent_area_selected))
    
    def select_full_screen_first(self):
        """Use full screen as the first step"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Create full screen area
        self.parent_area = {
            "x1": 0,
            "y1": 0,
            "x2": screen_width,
            "y2": screen_height
        }
        
        # Move to step 2
        self.start_sub_area_selection()
    
    def select_manual_area_first(self):
        """Select a manual area as the first step"""
        # Hide main window
        self.root.withdraw()
        
        # Create manual area selector
        self.create_manual_selector(self.on_parent_area_selected)
    
    def on_parent_area_selected(self, area):
        """Handle selection of parent area (step 1)"""
        print(f"Parent area selected: {area}")  # Debug output
        
        if not area:
            # Selection was cancelled
            self.root.deiconify()
            return
        
        # Store the parent area immediately
        self.parent_area = area
        
        # Schedule the sub-area selection with a slight delay to avoid race conditions
        try:
            # Use after to ensure UI has time to update
            self.root.after(200, self._start_sub_area_selection_wrapper)
        except Exception as e:
            # If there's an error during the transition to step 2
            import traceback
            traceback.print_exc()
            
            # Show error to user
            tk.messagebox.showerror(
                "Error",
                f"An error occurred scheduling the second step: {str(e)}\n\n"
                "Try selecting a different window or using manual selection instead."
            )
            
            # Show main window again
            self.root.deiconify()
    
    def _start_sub_area_selection_wrapper(self):
        """Wrapper to safely call start_sub_area_selection with error handling"""
        try:
            self.start_sub_area_selection()
        except Exception as e:
            # If there's an error during the transition to step 2
            import traceback
            traceback.print_exc()
            
            # Show error to user
            tk.messagebox.showerror(
                "Error",
                f"An error occurred preparing the second step: {str(e)}\n\n"
                "Try selecting a different window or using manual selection instead."
            )
            
            # Show main window again
            self.root.deiconify()
    
    def start_sub_area_selection(self):
        """Start the second step: selecting a sub-area"""
        # First ensure no grabs are active
        try:
            self.root.grab_release()
        except Exception:
            pass
            
        try:
            # Print debug info about parent area
            print(f"Starting sub-area selection with parent area: {self.parent_area}")
                
            # Create a dialog to confirm next step
            confirm_win = tk.Toplevel()  # Create independent of self.root to avoid grab issues
            confirm_win.title("Step 2 of 2 - Sub-Area Selection")
            confirm_win.geometry("450x200")
            confirm_win.attributes("-topmost", True)
            
            # Center the window on screen
            confirm_win.update_idletasks()
            width = confirm_win.winfo_width()
            height = confirm_win.winfo_height()
            x = (confirm_win.winfo_screenwidth() // 2) - (width // 2)
            y = (confirm_win.winfo_screenheight() // 2) - (height // 2)
            confirm_win.geometry(f"{width}x{height}+{x}+{y}")
            
            # Make it visible and active
            confirm_win.deiconify()
            confirm_win.update()
            
            # Try to make it modal without using grab
            confirm_win.focus_force()
            
            # Wait a moment before trying to set grab to avoid conflicts
            def try_set_grab():
                try:
                    confirm_win.grab_set()
                except Exception as e:
                    print(f"Non-critical: Could not set grab for confirmation dialog: {str(e)}")
            
            confirm_win.after(200, try_set_grab)
        except Exception as e:
            # If we can't create the dialog window
            tk.messagebox.showerror(
                "Error", 
                f"Could not create the sub-area selection dialog: {str(e)}\n\n"
                "Please try again or restart the application."
            )
            self.root.deiconify()
            return
        
        # Center on screen
        x = (confirm_win.winfo_screenwidth() // 2) - (400 // 2)
        y = (confirm_win.winfo_screenheight() // 2) - (150 // 2)
        confirm_win.geometry(f"+{x}+{y}")
        
        # Content frame
        frame = ttk.Frame(confirm_win, padding="10 10 10 10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress indicator
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            progress_frame,
            text="✓ Step 1: Window selected",
            foreground="green",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            progress_frame,
            text=" → Step 2: Select sub-area",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)
        
        # Main instruction
        ttk.Label(
            frame,
            text="Window Selected Successfully!",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            frame,
            text="Now you need to select the specific area within that window for OCR processing. You can either select a sub-area or use the entire window.",
            wraplength=430,
            justify=tk.LEFT
        ).pack(pady=5)
        
        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10, fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="Select Sub-Area Inside Window",
            command=lambda: self.proceed_to_sub_area_selection(confirm_win),
            width=25
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Use Entire Window",
            command=lambda: self.use_entire_area(confirm_win),
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=lambda: self.cancel_selection(confirm_win),
            width=10
        ).pack(side=tk.RIGHT, padx=5)
    
    def proceed_to_sub_area_selection(self, confirm_win):
        """Proceed to selecting a sub-area"""
        confirm_win.destroy()
        try:
            self.create_sub_area_selector()
        except Exception as e:
            # Handle errors during sub-area selection creation
            import traceback
            traceback.print_exc()
            
            # Show error to user
            tk.messagebox.showerror(
                "Error", 
                f"Failed to create sub-area selector: {str(e)}\n\n"
                "Try using 'Use Entire Window' option instead."
            )
            
            # Show the confirmation dialog again
            self.start_sub_area_selection()
    
    def use_entire_area(self, confirm_win):
        """Use the entire parent area"""
        confirm_win.destroy()
        if self.callback:
            self.callback(self.parent_area, self.parent_area)
        self.root.destroy()
    
    def cancel_selection(self, confirm_win):
        """Cancel the selection process"""
        confirm_win.destroy()
        self.root.deiconify()
    
    def create_sub_area_selector(self):
        """Create the sub-area selector within the parent area"""
        # Create a new window with a screenshot of the parent area
        try:
            # Release any existing grabs
            try:
                self.root.grab_release()
            except Exception:
                pass
                
            # Take screenshot of the parent area
            from ..capture.screenshot import ScreenCapture
            screen_capture = ScreenCapture()
            screenshot = screen_capture.capture_area(
                self.parent_area["x1"], self.parent_area["y1"], 
                self.parent_area["x2"], self.parent_area["y2"]
            )
            
            # Create a window for sub-area selection
            sub_win = tk.Toplevel()  # Create as independent window
            sub_win.title("Step 2: Select Sub-Area")
            sub_win.attributes("-topmost", True)
            
            # Don't use transient or grab which can cause issues
            sub_win.focus_force()
            
            # Size window to fit the screenshot
            img_width, img_height = screenshot.size
            screen_width = sub_win.winfo_screenwidth()
            screen_height = sub_win.winfo_screenheight()
            
            # Scale down if image is too large
            scale = 1.0
            if img_width > screen_width * 0.9 or img_height > screen_height * 0.9:
                scale_x = (screen_width * 0.9) / img_width
                scale_y = (screen_height * 0.9) / img_height
                scale = min(scale_x, scale_y)
                img_width = int(img_width * scale)
                img_height = int(img_height * scale)
                screenshot = screenshot.resize((img_width, img_height))
            
            # Set window size and position
            x = (screen_width // 2) - (img_width // 2)
            y = (screen_height // 2) - (img_height // 2)
            sub_win.geometry(f"{img_width}x{img_height}+{x}+{y}")
            
            # Convert screenshot for display
            from PIL import ImageTk
            screenshot_tk = ImageTk.PhotoImage(screenshot)
            
            # Create canvas for drawing selection
            canvas = tk.Canvas(sub_win, width=img_width, height=img_height)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Display the screenshot
            canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_tk)
            canvas.image = screenshot_tk  # Keep reference
            
            # Variables for selection rectangle
            start_x = 0
            start_y = 0
            rect_id = None
            
            # Instructions
            instruction_frame = tk.Frame(sub_win, bg="#333333", padx=10, pady=5)
            instruction_frame.place(x=10, y=10)
            
            instructions = tk.Label(
                instruction_frame,
                text="CLICK AND DRAG to select the OCR area\nPress ESC to cancel",
                bg="#333333",
                fg="white",
                font=("Arial", 12, "bold"),
                padx=5,
                pady=5
            )
            instructions.pack()
            
            # Add progress indicator
            progress_frame = tk.Frame(sub_win, bg="#333333", padx=10, pady=5)
            progress_frame.place(x=10, y=60)
            
            tk.Label(
                progress_frame,
                text="Step 2 of 2: Draw the exact area for OCR recognition",
                bg="#333333",
                fg="yellow",
                font=("Arial", 11),
                padx=5,
                pady=5
            ).pack()
            
            # Event handlers for mouse
            def on_press(event):
                nonlocal start_x, start_y, rect_id
                start_x = event.x
                start_y = event.y
                
                if rect_id:
                    canvas.delete(rect_id)
                
                rect_id = canvas.create_rectangle(
                    start_x, start_y, start_x, start_y,
                    outline="red", width=2
                )
            
            def on_drag(event):
                nonlocal rect_id
                x, y = event.x, event.y
                
                # Keep within bounds
                x = max(0, min(x, img_width))
                y = max(0, min(y, img_height))
                
                # Update rectangle
                canvas.coords(rect_id, start_x, start_y, x, y)
            
            def on_release(event):
                try:
                    # Calculate sub-area coordinates
                    x, y = event.x, event.y
                    
                    # Keep within bounds
                    x = max(0, min(x, img_width))
                    y = max(0, min(y, img_height))
                    
                    # Convert coordinates from scaled to original
                    x1_scaled = min(start_x, x)
                    y1_scaled = min(start_y, y)
                    x2_scaled = max(start_x, x)
                    y2_scaled = max(start_y, y)
                    
                    # Convert back to original parent area coordinates
                    if scale != 1.0:
                        x1_orig = int(x1_scaled / scale) + self.parent_area["x1"]
                        y1_orig = int(y1_scaled / scale) + self.parent_area["y1"]
                        x2_orig = int(x2_scaled / scale) + self.parent_area["x1"]
                        y2_orig = int(y2_scaled / scale) + self.parent_area["y1"]
                    else:
                        x1_orig = x1_scaled + self.parent_area["x1"]
                        y1_orig = y1_scaled + self.parent_area["y1"]
                        x2_orig = x2_scaled + self.parent_area["x1"]
                        y2_orig = y2_scaled + self.parent_area["y1"]
                    
                    # Create sub-area dict
                    sub_area = {
                        "x1": x1_orig,
                        "y1": y1_orig,
                        "x2": x2_orig,
                        "y2": y2_orig
                    }
                    
                    # Store the sub-area for later callback
                    selected_sub_area = sub_area
                    
                    # Schedule window destruction and callback
                    sub_win.after(100, lambda: complete_selection(sub_area))
                except Exception as e:
                    print(f"Error in sub-area selection: {str(e)}")
                    # Close the window
                    sub_win.destroy()
                    # Show main window again
                    self.root.deiconify()
            
            def complete_selection(sub_area):
                try:
                    # Close the sub-window
                    sub_win.destroy()
                    
                    # Ensure we can safely destroy the main window
                    # by scheduling it after this event completes
                    self.root.after(100, lambda: finish_with_callback(sub_area))
                except Exception as e:
                    print(f"Error completing selection: {str(e)}")
                    self.root.deiconify()
            
            def finish_with_callback(sub_area):
                try:
                    # Call the callback with both areas
                    if self.callback:
                        self.callback(self.parent_area, sub_area)
                    
                    # Close the main window
                    self.root.destroy()
                except Exception as e:
                    print(f"Error in callback: {str(e)}")
                    self.root.deiconify()
            
            # Bind events
            canvas.bind("<ButtonPress-1>", on_press)
            canvas.bind("<B1-Motion>", on_drag)
            canvas.bind("<ButtonRelease-1>", on_release)
            sub_win.bind("<Escape>", lambda e: self.cancel_sub_selection(sub_win))
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to create sub-area selector: {str(e)}")
            self.root.deiconify()
    
    def cancel_sub_selection(self, sub_win):
        """Cancel the sub-area selection"""
        sub_win.destroy()
        self.root.deiconify()
    
    def create_manual_selector(self, callback):
        """Create a manual area selector overlay"""
        # Create fullscreen transparent window
        select_win = tk.Toplevel(self.root)
        select_win.attributes("-alpha", 0.3)
        select_win.attributes("-fullscreen", True)
        select_win.attributes("-topmost", True)
        
        # Canvas for drawing
        canvas = tk.Canvas(select_win, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Variables for selection
        start_x = 0
        start_y = 0
        rect_id = None
        
        # Instructions
        instruction_frame = tk.Frame(select_win, bg="#333333", padx=10, pady=10)
        instruction_frame.place(x=10, y=10)
        
        instructions = tk.Label(
            instruction_frame,
            text="Click and drag to select an area. Press Escape to cancel.",
            bg="#333333",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=10,
            pady=10
        )
        instructions.pack()
        
        # Event handlers
        def on_press(event):
            nonlocal start_x, start_y, rect_id
            start_x = event.x
            start_y = event.y
            
            if rect_id:
                canvas.delete(rect_id)
            
            rect_id = canvas.create_rectangle(
                start_x, start_y, start_x, start_y,
                outline="red", width=2
            )
        
        def on_drag(event):
            nonlocal rect_id
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)
        
        def on_release(event):
            # Calculate coordinates
            x1 = min(start_x, event.x)
            y1 = min(start_y, event.y)
            x2 = max(start_x, event.x)
            y2 = max(start_y, event.y)
            
            area = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }
            
            # Close the window
            select_win.destroy()
            
            # Call the callback
            if callback:
                callback(area)
        
        def on_cancel(event):
            select_win.destroy()
            if callback:
                callback(None)
        
        # Bind events
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        select_win.bind("<Escape>", on_cancel)
    
    def run(self):
        """Run the two-step area selector"""
        self.root.mainloop()

class WindowSelector(simpledialog.Dialog):
    """Dialog to select a window from a list of all visible windows"""
    
    def __init__(self, parent, title=None, callback=None):
        """
        Initialize the window selector dialog.
        
        Args:
            parent: The parent window
            title: Dialog title
            callback: Function to call with selected window coordinates
        """
        self.callback = callback
        self.window_list = []
        self.selected_window = None
        
        # Check if window selection is supported
        if not HAS_WINDOW_SUPPORT:
            tk.messagebox.showerror(
                "Feature Not Available", 
                "Window selection requires the pygetwindow package. Please install it with: pip install pygetwindow"
            )
            return
        
        # Get all visible windows
        try:
            all_windows = gw.getAllWindows()
            # Filter out tiny or hidden windows
            self.window_list = [w for w in all_windows if w.width > 50 and w.height > 50 and w.title]
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to get window list: {str(e)}")
            return
            
        # Release any grabs from parent
        try:
            if parent:
                parent.grab_release()
        except Exception:
            pass
            
        # Call parent constructor but handle exceptions
        try:
            super().__init__(parent, title)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to create window selector: {str(e)}")
            if parent:
                parent.deiconify()
    
    def body(self, master):
        """Create dialog body. Return widget that should have initial focus"""
        # Instruction text
        ttk.Label(
            master, 
            text="Select the window containing the game or application to capture:",
            wraplength=400
        ).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        # Create a frame with scrollbar for the window list
        list_frame = ttk.Frame(master)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # Create scrollbars
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the listbox with windows
        self.listbox = tk.Listbox(
            list_frame,
            width=60,
            height=15,
            yscrollcommand=scrollbar_y.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar_y.config(command=self.listbox.yview)
        
        # Add windows to the list
        for window in self.window_list:
            self.listbox.insert(tk.END, f"{window.title} ({window.width}x{window.height})")
        
        # Add a refresh button
        ttk.Button(
            master, 
            text="Refresh Window List", 
            command=self.refresh_windows,
            width=15
        ).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        
        # Bind Escape key to cancel
        self.bind("<Escape>", lambda e: self.cancel())
        
        # Add a preview checkbox
        self.preview_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            master, 
            text="Highlight selected window before capturing", 
            variable=self.preview_var
        ).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        
        # Add help text
        help_text = "The selected window will be used as the capture area for OCR analysis"
        ttk.Label(
            master, 
            text=help_text, 
            foreground="gray", 
            wraplength=400
        ).grid(row=4, column=0, sticky='w', padx=5, pady=5)
        
        return self.listbox  # Initial focus on listbox
    
    def refresh_windows(self):
        """Refresh the window list"""
        if not HAS_WINDOW_SUPPORT:
            return
            
        try:
            # Clear current list
            self.listbox.delete(0, tk.END)
            self.window_list = []
            
            # Get all visible windows
            all_windows = gw.getAllWindows()
            # Filter out tiny or hidden windows
            self.window_list = [w for w in all_windows if w.width > 50 and w.height > 50 and w.title]
            
            # Add windows to the list
            for window in self.window_list:
                self.listbox.insert(tk.END, f"{window.title} ({window.width}x{window.height})")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to refresh window list: {str(e)}")
    
    def apply(self):
        """Called when OK button is clicked"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.window_list):
                self.selected_window = self.window_list[index]
                
                # Check if we should highlight the window first
                highlight_window = self.preview_var.get()
                
                # Make sure we have a reference to the parent window before destroying this dialog
                parent = self.master
                
                # Close this dialog before highlighting to prevent UI freeze
                try:
                    self.destroy()
                except Exception as e:
                    print(f"Non-critical error destroying window selector: {e}")
                
                # Get window coordinates first to ensure we have them before highlighting
                try:
                    area = {
                        "x1": self.selected_window.left,
                        "y1": self.selected_window.top,
                        "x2": self.selected_window.left + self.selected_window.width,
                        "y2": self.selected_window.top + self.selected_window.height
                    }
                    
                    # Highlight after closing the dialog to prevent UI freeze
                    if highlight_window:
                        try:
                            self.highlight_window(self.selected_window)
                        except Exception as e:
                            print(f"Error highlighting window (non-fatal): {str(e)}")
                    
                    # Callback will be called after dialog is closed and optional highlighting
                    # Use after to give the UI thread time to process and avoid race conditions
                    if self.callback:
                        if self.master:
                            self.master.after(100, lambda: self.callback(area))
                        else:
                            self.callback(area)
                except Exception as e:
                    # Show error before closing dialog
                    tk.messagebox.showerror("Error", f"Failed to get window coordinates: {str(e)}")
                    self.destroy()
    
    def cancel(self):
        """Cancel the window selection"""
        self.selected_window = None
        self.destroy()
        
    def highlight_window(self, window):
        """Highlight the selected window briefly"""
        try:
            # Create a fullscreen transparent window
            highlight = tk.Toplevel()
            highlight.attributes("-alpha", 0.3)
            highlight.attributes("-topmost", True)
            highlight.overrideredirect(True)
            
            # Position and size it to match the selected window
            # Ensure valid dimensions
            width = max(10, window.width)
            height = max(10, window.height)
            left = max(0, window.left)
            top = max(0, window.top)
            
            highlight.geometry(f"{width}x{height}+{left}+{top}")
            
            # Create a red border canvas with a default background color
            canvas = tk.Canvas(
                highlight, 
                bg="white",  # Default fallback color
                highlightthickness=4, 
                highlightbackground="red"
            )
            canvas.pack(fill=tk.BOTH, expand=True)
            
            try:
                # Try to make the background transparent/match system color
                # This is platform-dependent
                canvas.configure(bg="SystemButtonFace")
            except tk.TclError:
                # If that fails, try another approach
                try:
                    canvas.configure(bg="#F0F0F0")  # Light gray as fallback
                except:
                    pass  # Keep the white background if all else fails
            
            # Add a visible message so user knows what happened
            canvas.create_text(
                width // 2, height // 2,
                text="Window selected!",
                fill="red",
                font=("Arial", 14, "bold")
            )
            
            # Show for 1.5 seconds then destroy
            highlight.after(1500, highlight.destroy)
            
            # Update to show the highlight
            highlight.update()
        except Exception as e:
            print(f"Error highlighting window: {str(e)}")
            # Continue with the process even if highlighting fails

class AreaSelector:
    """Area selection UI class"""
    
    def __init__(self, root: Optional[tk.Tk] = None, callback: Optional[Callable[[Dict[str, int]], None]] = None):
        """
        Initialize the area selector UI.
        
        Args:
            root: Tkinter root window. If None, creates a new one.
            callback: Function to call with selected area when done
        """
        self.callback = callback
        
        # Create a new root window if none provided
        if root is None:
            self.root = tk.Tk()
            self.root.title("Select Capture Method")
            self.root.geometry("450x220")
            self.owns_root = True
        else:
            self.root = root
            self.owns_root = False
        
        # Create the selection mode UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the initial UI for choosing selection mode"""
        frame = ttk.Frame(self.root, padding="10 10 10 10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            frame, 
            text="Choose Capture Method", 
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))
        
        # Instructions
        ttk.Label(
            frame,
            text="Select a specific window or draw a custom area",
            wraplength=380
        ).pack(pady=(0, 15))
        
        # Select window button
        self.window_btn = ttk.Button(
            frame,
            text="Select Specific Window",
            command=self.show_window_selector,
            width=30
        )
        self.window_btn.pack(pady=5)
        
        # Manual selection button
        ttk.Button(
            frame,
            text="Draw Custom Area Selection",
            command=self.show_manual_selector,
            width=30
        ).pack(pady=5)
        
        # Disable window selection if not supported
        if not HAS_WINDOW_SUPPORT:
            self.window_btn.config(state=tk.DISABLED)
            ttk.Label(
                frame,
                text="Window selection requires pygetwindow package",
                foreground="red"
            ).pack(pady=5)
    
    def show_window_selector(self):
        """Show the window selector dialog"""
        # Release any existing grabs first
        try:
            self.root.grab_release()
        except Exception:
            pass
            
        # Hide the main selector window temporarily
        self.root.withdraw()
        
        # Create and show the window selector
        # Note: The dialog will handle callbacks and window management itself
        try:
            # Give a small delay to ensure window management operations complete
            self.root.after(100, self._create_window_selector)
        except Exception as e:
            # If there's an error, show the main window again
            print(f"Error setting up window selector: {str(e)}")
            self.root.deiconify()
    
    def _create_window_selector(self):
        """Create the window selector dialog with proper timing"""
        try:
            selector = WindowSelector(self.root, "Select Window", self.on_parent_area_selected)
        except Exception as e:
            # If there's an error creating the window selector, show the main window again
            print(f"Error creating window selector: {str(e)}")
            self.root.deiconify()
    
    def show_manual_selector(self):
        """Show the manual area selector"""
        # Hide the main selector window
        self.root.withdraw()
        
        # Create a new fullscreen transparent window for manual selection
        select_win = tk.Toplevel(self.root)
        select_win.title("Manual Area Selection")
        select_win.attributes("-alpha", 0.3)
        select_win.attributes("-fullscreen", True)
        select_win.attributes("-topmost", True)
        
        # Create a canvas covering the full screen
        canvas = tk.Canvas(select_win, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Variables to store rectangle coordinates
        start_x = 0
        start_y = 0
        rectangle_id = None
        
        # Instructions - make it more visible with a better background and larger font
        instruction_frame = tk.Frame(select_win, bg="#333333", padx=10, pady=10)
        instruction_frame.place(x=10, y=10)
        
        instructions = tk.Label(
            instruction_frame,
            text="Click and drag to select an area. Press Escape to cancel.",
            bg="#333333",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=10,
            pady=10
        )
        instructions.pack()
        
        # Define event handlers
        def on_press(event):
            nonlocal start_x, start_y, rectangle_id
            start_x = event.x
            start_y = event.y
            
            # Create a new rectangle if it doesn't exist
            if rectangle_id:
                canvas.delete(rectangle_id)
            
            rectangle_id = canvas.create_rectangle(
                start_x, start_y, start_x, start_y,
                outline="red", width=2
            )
        
        def on_drag(event):
            nonlocal rectangle_id
            end_x = event.x
            end_y = event.y
            
            # Update rectangle size
            canvas.coords(rectangle_id, start_x, start_y, end_x, end_y)
        
        def on_release(event):
            end_x = event.x
            end_y = event.y
            
            # Ensure coordinates are ordered properly (top-left to bottom-right)
            x1 = min(start_x, end_x)
            y1 = min(start_y, end_y)
            x2 = max(start_x, end_x)
            y2 = max(start_y, end_y)
            
            selected_area = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }
            
            # Close the selection window
            select_win.destroy()
            
            # Call the completion handler
            self.on_selection_complete(selected_area)
        
        def on_cancel(event):
            # Close the selection window
            select_win.destroy()
            
            # Show the main selector window again
            self.root.deiconify()
        
        # Bind events
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        select_win.bind("<Escape>", on_cancel)
    
    def on_selection_complete(self, area):
        """Handle completion of area selection"""
        # Close the main window if we own it
        if self.owns_root:
            self.root.destroy()
        else:
            # Just hide the selector
            self.root.withdraw()
        
        # Call the callback with the selected area
        if self.callback and area:
            self.callback(area)
    
    def cancel(self):
        """Cancel the selection and close the window"""
        # For backward compatibility
        if self.callback:
            self.callback(None)
        
        if self.owns_root:
            self.root.destroy()
        else:
            # Just hide the selector
            self.root.withdraw()
    
    def run(self) -> None:
        """Run the area selector"""
        if self.owns_root:
            self.root.mainloop()
    
    def on_press(self, event):
        """Handle mouse button press"""
        self.start_x = event.x
        self.start_y = event.y
        
        # Create a new rectangle if it doesn't exist
        if self.rectangle_id:
            self.canvas.delete(self.rectangle_id)
        
        self.rectangle_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )
    
    def on_drag(self, event):
        """Handle mouse drag"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Update rectangle size
        self.canvas.coords(self.rectangle_id, self.start_x, self.start_y, self.end_x, self.end_y)
    
    def on_release(self, event):
        """Handle mouse button release"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Ensure coordinates are ordered properly (top-left to bottom-right)
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        selected_area = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        
        # Call the callback with the selected area
        if self.callback:
            self.callback(selected_area)
        
        # Close the window if we own it
        if self.owns_root:
            self.root.destroy()
        else:
            # Just hide the selector
            self.canvas.pack_forget()
            self.instructions.place_forget()
    
    def cancel(self):
        """Cancel the selection and close the window"""
        if self.callback:
            self.callback(None)
        
        if self.owns_root:
            self.root.destroy()
        else:
            # Just hide the selector
            self.canvas.pack_forget()
            self.instructions.place_forget()
    
    def run(self) -> None:
        """Run the area selector"""
        if self.owns_root:
            self.root.mainloop()
