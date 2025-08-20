"""
Area selection UI module for Tap Ninja Helper.
Allows users to select screen areas for capture and OCR.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, Tuple

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
            self.root.title("Select Area")
            self.owns_root = True
        else:
            self.root = root
            self.owns_root = False
        
        # Make window transparent for screenshot
        self.root.attributes("-alpha", 0.3)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        
        # Create a canvas covering the full screen
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Variables to store rectangle coordinates
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.rectangle_id = None
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Bind Escape key to cancel
        self.root.bind("<Escape>", lambda event: self.cancel())
        
        # Instructions
        self.instructions = tk.Label(
            self.root,
            text="Click and drag to select an area. Press Escape to cancel.",
            bg="white",
            fg="black",
            font=("Arial", 12)
        )
        self.instructions.place(x=10, y=10)
    
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
