import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional
import os
from pathlib import Path


class MarkdownCombiner(tk.Tk):
    """A GUI application for selecting, arranging, and combining markdown files."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Markdown File Combiner")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        self.selected_files: List[str] = []
        
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Set up the user interface components."""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add files button
        add_btn = ttk.Button(btn_frame, text="Add Files", command=self.add_files)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove selected button
        remove_btn = ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear all button
        clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Generate button
        generate_btn = ttk.Button(btn_frame, text="Generate Combined File", command=self.generate_combined_file)
        generate_btn.pack(side=tk.RIGHT, padx=5)
        
        # Files list with scrollbar
        list_frame = ttk.LabelFrame(main_frame, text="Drag files to reorder")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.files_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        # Configure drag and drop functionality
        self.files_listbox.bind('<Button-1>', self.on_click)
        self.files_listbox.bind('<B1-Motion>', self.on_drag)
        self.files_listbox.bind('<ButtonRelease-1>', self.on_drop)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def add_files(self) -> None:
        """Open file dialog to select markdown files."""
        files = filedialog.askopenfilenames(
            title="Select Markdown Files",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if not files:
            return
            
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))
        
        self.status_var.set(f"{len(self.selected_files)} files loaded")
    
    def remove_selected(self) -> None:
        """Remove the selected file from the list."""
        selected = self.files_listbox.curselection()
        if not selected:
            return
            
        index = selected[0]
        self.files_listbox.delete(index)
        self.selected_files.pop(index)
        self.status_var.set(f"{len(self.selected_files)} files remaining")
    
    def clear_all(self) -> None:
        """Clear all files from the list."""
        self.files_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self.status_var.set("All files cleared")
    
    def on_click(self, event: tk.Event) -> None:
        """Handle click event to prepare for drag and drop."""
        # Save the selected item index
        self.drag_start_index = self.files_listbox.nearest(event.y)
        if self.drag_start_index < 0 or self.drag_start_index >= self.files_listbox.size():
            return
            
        # Select the item
        self.files_listbox.selection_clear(0, tk.END)
        self.files_listbox.selection_set(self.drag_start_index)
        self.files_listbox.activate(self.drag_start_index)
    
    def on_drag(self, event: tk.Event) -> None:
        """Handle drag motion event."""
        pass  # We just need to track the mouse, the actual reordering happens on drop
    
    def on_drop(self, event: tk.Event) -> None:
        """Handle drop event to reorder items."""
        drop_index = self.files_listbox.nearest(event.y)
        
        if drop_index < 0 or drop_index >= self.files_listbox.size() or drop_index == self.drag_start_index:
            return
            
        # Get the text and file of the dragged item
        text = self.files_listbox.get(self.drag_start_index)
        file = self.selected_files[self.drag_start_index]
        
        # Remove from original position
        self.files_listbox.delete(self.drag_start_index)
        self.selected_files.pop(self.drag_start_index)
        
        # Insert at new position
        self.files_listbox.insert(drop_index, text)
        self.selected_files.insert(drop_index, file)
        
        # Reselect the moved item
        self.files_listbox.selection_clear(0, tk.END)
        self.files_listbox.selection_set(drop_index)
        self.files_listbox.activate(drop_index)
        
        self.status_var.set(f"Moved '{text}' to position {drop_index + 1}")
    
    def generate_combined_file(self) -> None:
        """Generate a combined markdown file from selected files in the current order."""
        if not self.selected_files:
            messagebox.showwarning("No Files", "No markdown files have been added.")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save Combined Markdown File",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
            
        try:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                for file_path in self.selected_files:
                    file_name = os.path.basename(file_path)
                    outfile.write(f"\n\n<!-- File: {file_name} -->\n\n")
                    
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
            
            self.status_var.set(f"Successfully combined {len(self.selected_files)} files to {output_file}")
            messagebox.showinfo("Success", f"Combined markdown file created at:\n{output_file}")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to create combined file:\n{str(e)}")


if __name__ == "__main__":
    app = MarkdownCombiner()
    app.mainloop()
