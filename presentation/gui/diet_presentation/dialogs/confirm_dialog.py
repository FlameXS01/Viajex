import tkinter as tk
from tkinter import ttk

class ConfirmDialog(tk.Toplevel):
    """
    Diálogo de confirmación genérico
    """
    
    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.result = False
        
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets(message)
        self.center_on_parent(parent)
    
    def create_widgets(self, message: str):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje
        ttk.Label(main_frame, text=message, wraplength=250).pack(pady=(10, 20))
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Sí", command=self.on_yes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="No", command=self.on_no).pack(side=tk.RIGHT)
    
    def center_on_parent(self, parent):
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def on_yes(self):
        self.result = True
        self.destroy()
    
    def on_no(self):
        self.destroy()