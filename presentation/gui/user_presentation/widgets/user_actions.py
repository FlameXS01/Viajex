import tkinter as tk
from tkinter import ttk

class UserActions(ttk.Frame):
    """Panel de acciones para usuarios seleccionados"""
    
    def __init__(self, parent, action_callbacks, **kwargs):
        """
        Args:
            parent: Widget padre
            action_callbacks: Diccionario con funciones callback para cada acción
        """
        super().__init__(parent, **kwargs)
        self.action_callbacks = action_callbacks
        self.buttons = {}
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea los botones de acción"""
        actions = [
            ("Editar Usuario", "edit"),
            ("Cambiar Rol", "change_role"),
            ("Cambiar Password", "change_password"),
            ("Activar/Desactivar", "toggle_active"),
            ("Eliminar Usuario", "delete")
        ]
        
        for i, (text, action) in enumerate(actions):
            btn = ttk.Button(self, text=text, 
                           command=lambda a=action: self._on_action(a),
                           state=tk.DISABLED)
            btn.grid(row=0, column=i, padx=5, pady=5)
            self.buttons[action] = btn

    def _on_action(self, action):
        """Ejecuta la callback correspondiente a la acción"""
        if action in self.action_callbacks:
            self.action_callbacks[action]()

    def set_buttons_state(self, state):
        """Establece el estado de todos los botones"""
        for btn in self.buttons.values():
            btn.config(state=state)