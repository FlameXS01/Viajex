import tkinter as tk
from tkinter import ttk
from presentation.gui.utils.windows_utils import WindowUtils

class ConfirmDialog:
    """Diálogo de confirmación para acciones destructivas"""
    
    def __init__(self, parent, title, message, confirm_callback):
        self.confirm_callback = confirm_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x175")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        WindowUtils.center_window(self.dialog, parent)
        self._create_widgets(message)

    def _create_widgets(self, message):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=message, wraplength=350).pack(pady=10, expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Confirmar", command=self._confirm).grid(row=0, column=1, padx=5)

    def _confirm(self):
        """Ejecuta la callback de confirmación"""
        self.confirm_callback()
        self.dialog.destroy()