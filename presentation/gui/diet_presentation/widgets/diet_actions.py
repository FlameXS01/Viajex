import tkinter as tk
from tkinter import ttk

class DietActions(ttk.Frame):
    """
    Widget con los botones de acciones para el módulo de dietas
    """
    
    def __init__(self, parent, module):
        super().__init__(parent)
        self.module = module
        
        self.create_widgets()
        self.update_buttons_state(None)
    
    def create_widgets(self):
        # Frame para botones principales
        main_buttons_frame = ttk.Frame(self)
        main_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones principales
        self.create_btn = ttk.Button(main_buttons_frame, text="Crear Dieta", 
                                   command=self.module.create_diet)
        self.create_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_btn = ttk.Button(main_buttons_frame, text="Editar Dieta", 
                                 command=self.module.edit_diet)
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_btn = ttk.Button(main_buttons_frame, text="Eliminar Dieta", 
                                   command=self.module.delete_diet)
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.liquidate_btn = ttk.Button(main_buttons_frame, text="Liquidar Dieta", 
                                      command=self.module.liquidate_diet)
        self.liquidate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame para botones secundarios
        secondary_buttons_frame = ttk.Frame(self)
        secondary_buttons_frame.pack(fill=tk.X)
        
        # Botón de actualizar
        self.refresh_btn = ttk.Button(secondary_buttons_frame, text="Actualizar Lista", 
                                    command=self.module.refresh_diets)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Contadores
        self.counters_label = ttk.Label(secondary_buttons_frame, text="Anticipos: 0 | Liquidaciones: 0")
        self.counters_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Llamar a refresh_counters después de crear los widgets
        self.refresh_counters()
    
    def update_buttons_state(self, selected_diet):
        """
        Actualiza el estado de los botones según la dieta seleccionada
        """
        
        if selected_diet is None:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.liquidate_btn.config(state=tk.DISABLED)
        else:
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            
            # Solo se puede liquidar si está en estado REQUESTED
            if selected_diet.status == "requested": 
                self.liquidate_btn.config(state=tk.NORMAL)
            else:
                self.liquidate_btn.config(state=tk.DISABLED)
            
    
    def refresh_counters(self):
        """Actualiza los contadores en la interfaz"""
        try:
            # CORREGIDO: Llamar al método del módulo en lugar de diet_controller
            counters = self.module.get_counters_info()
            self.counters_label.config(
                text=f"Anticipos: {counters.total_advance_number} | Liquidaciones: {counters.total_liquidation_number}"
            )
        except Exception as e:
            print(f"ERROR refrescando contadores: {e}")
            self.counters_label.config(text="Anticipos: 0 | Liquidaciones: 0")