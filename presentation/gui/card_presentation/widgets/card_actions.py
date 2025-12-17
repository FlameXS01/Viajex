import tkinter as tk
from tkinter import ttk

class CardActions(ttk.Frame):
    """Panel de acciones para tarjetas - Versión simplificada"""
    
    def __init__(self, parent, actions):
        super().__init__(parent)
        self.actions = actions
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea botones de acción"""
        # Botón Recargar
        if 'recharge' in self.actions:
            self.recharge_btn = ttk.Button(
                self,
                text="Recargar",
                command=self.actions['recharge'],
                width=12
            )
            self.recharge_btn.pack(side=tk.LEFT, padx=2)
        
        # Botón Editar
        if 'edit' in self.actions:
            self.edit_btn = ttk.Button(
                self,
                text="Editar",
                command=self.actions['edit'],
                width=12
            )
            self.edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Botón Estado
        if 'toggle_active' in self.actions:
            self.toggle_btn = ttk.Button(
                self,
                text="Estado",
                command=self.actions['toggle_active'],
                width=12
            )
            self.toggle_btn.pack(side=tk.LEFT, padx=2)
        
        # Botón Historial
        if 'view_history' in self.actions:
            self.history_btn = ttk.Button(
                self,
                text="Historial",
                command=self.actions['view_history'],
                width=12
            )
            self.history_btn.pack(side=tk.LEFT, padx=2)
        
        # Botón Eliminar
        if 'delete' in self.actions:
            self.delete_btn = ttk.Button(
                self,
                text="Eliminar",
                command=self.actions['delete'],
                width=12
            )
            self.delete_btn.pack(side=tk.LEFT, padx=2)
    
    def set_buttons_state(self, state):
        """Habilita/deshabilita todos los botones"""
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state=state)