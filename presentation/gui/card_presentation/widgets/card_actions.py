import tkinter as tk
from tkinter import ttk

class CardActions(ttk.Frame):
    """Botones de acciones para tarjetas"""
    
    def __init__(self, parent, actions):
        super().__init__(parent)
        self.actions = actions
        self._create_widgets()

    def _create_widgets(self):
        """Crea los botones de acciones"""
        self.edit_btn = ttk.Button(self, text="Editar Tarjeta", 
                                command=self.actions['edit'])
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.toggle_btn = ttk.Button(self, text="Activar/Desactivar", 
                                    command=self.actions['toggle_active'])
        self.toggle_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(self, text="Eliminar Tarjeta", 
                                    command=self.actions['delete'])
        self.delete_btn.pack(side=tk.LEFT, padx=5)

    def set_buttons_state(self, state):
        """Habilita o deshabilita los botones"""
        self.edit_btn.config(state=state)
        self.toggle_btn.config(state=state)
        self.delete_btn.config(state=state)