import tkinter as tk
from tkinter import ttk

class ConfirmDialog:
    """Diálogo de confirmación simple"""
    
    def __init__(self, parent, title, message, on_confirm, 
                 confirm_text="Aceptar", cancel_text="Cancelar"):
        self.parent = parent
        self.on_confirm = on_confirm
        
        self._create_dialog(title, message, confirm_text, cancel_text)
    
    def _create_dialog(self, title, message, confirm_text, cancel_text):
        """Crea el diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # Centrar
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"+{x}+{y}")
        
        # Contenido
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icono de advertencia (opcional)
        warning_label = ttk.Label(main_frame, text="⚠️", font=('Arial', 24))
        warning_label.pack(pady=(0, 10))
        
        # Mensaje
        message_label = ttk.Label(
            main_frame, 
            text=message, 
            wraplength=350,
            justify=tk.CENTER
        )
        message_label.pack(fill=tk.X, pady=(0, 20))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text=confirm_text,
            command=self._on_confirm
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text=cancel_text,
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _on_confirm(self):
        """Ejecuta la acción de confirmación"""
        try:
            self.on_confirm()
        finally:
            self.dialog.destroy()