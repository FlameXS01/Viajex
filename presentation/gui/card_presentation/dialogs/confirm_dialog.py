import tkinter as tk
from tkinter import ttk

class ConfirmDialog:
    """Diálogo de confirmación genérico - VERSIÓN MEJORADA"""
    
    def __init__(self, parent, title, message, on_confirm, confirm_text="Confirmar", cancel_text="Cancelar"):
        self.parent = parent
        self.on_confirm = on_confirm
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        
        self._create_dialog(title, message)

    def _create_dialog(self, title, message):
        """Crea el diálogo de confirmación"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(title)
        self.dialog.geometry("450x180") 
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_widgets(message)

    def _create_widgets(self, message):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icono de advertencia (opcional)
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Mensaje
        message_label = ttk.Label(main_frame, text=message, wraplength=400, justify=tk.LEFT)
        message_label.pack(pady=(10, 20))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text=self.confirm_text, 
                    command=self._confirm).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text=self.cancel_text, 
                    command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _confirm(self):
        """Ejecuta la acción de confirmación y cierra el diálogo"""
        self.on_confirm()
        self.dialog.destroy()