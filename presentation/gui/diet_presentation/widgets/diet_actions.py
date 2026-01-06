import json

import tkinter as tk
from tkinter import ttk, messagebox

class DietActions(ttk.Frame):
    """
    Widget con los botones de acciones para el módulo de dietas
    """
    
    def __init__(self, parent, module):
        super().__init__(parent)
        self.module = module
        self.search_var = tk.StringVar()
        
        self.create_widgets()
        self.update_buttons_state(None)
    
    def create_widgets(self):
        # Frame principal para los botones de acciones
        main_buttons_frame = ttk.Frame(self)
        main_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones principales de acciones de dieta
        self.create_btn = ttk.Button(main_buttons_frame, text="Crear Dieta", 
                                    command=self.module.create_diet)
        self.create_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_btn = ttk.Button(main_buttons_frame, text="Editar Dieta", 
                                    command=self.module.edit_item)
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_btn = ttk.Button(main_buttons_frame, text="Eliminar Dieta", 
                                    command=self.module.delete_item)
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.liquidate_btn = ttk.Button(main_buttons_frame, text="Liquidar Dieta", 
                                    command=self.module.liquidate_diet)
        self.liquidate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame para el buscador
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Etiqueta y campo de búsqueda
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            width=40
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        # Insertar texto de ayuda
        self.search_entry.insert(0, "Buscar en todas las columnas...")
        self.search_entry.config(foreground="gray")
        
        # Bind eventos para el placeholder
        self.search_entry.bind('<FocusIn>', self._clear_placeholder)
        self.search_entry.bind('<FocusOut>', self._set_placeholder)
        
        # Botón para limpiar búsqueda
        self.clear_search_btn = ttk.Button(
            search_frame, 
            text="Limpiar", 
            command=self._clear_search,
            state=tk.DISABLED
        )
        self.clear_search_btn.pack(side=tk.LEFT)
        
        # Botón Gestionar Servicios (NUEVO)
        
        self.services_btn = ttk.Button(
            main_buttons_frame,
            text="Gestionar Servicios",
            command=self.module._manage_services,  # Debe apuntar al método en DietModule
            width=18
                                    )
        self.services_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para botones secundarios
        secondary_buttons_frame = ttk.Frame(self)
        secondary_buttons_frame.pack(fill=tk.X)
        
        # Botón de actualizar
        self.refresh_btn = ttk.Button(secondary_buttons_frame, text="Actualizar Lista", 
                                    command=self._refresh_with_search)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Contadores
        self.counters_label = ttk.Label(secondary_buttons_frame, text="Anticipos: 0 | Liquidaciones: 0")
        self.counters_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Llamar a refresh_counters después de crear los widgets
        self.refresh_counters()
    
    def _clear_placeholder(self, event=None):
        """Limpia el texto de ayuda cuando el campo recibe foco"""
        if self.search_entry.get() == "Buscar en todas las columnas...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground="black")
    
    def _set_placeholder(self, event=None):
        """Establece el texto de ayuda si el campo está vacío"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "Buscar en todas las columnas...")
            self.search_entry.config(foreground="gray")
    
    def _on_search(self, event=None):
        """Maneja la búsqueda en tiempo real"""
        # Ignorar si es el texto de ayuda
        if self.search_entry.get() == "Buscar en todas las columnas...":
            search_text = ""
        else:
            search_text = self.search_var.get().strip()
        
        # Actualizar estado del botón limpiar
        if search_text:
            self.clear_search_btn.config(state=tk.NORMAL)
        else:
            self.clear_search_btn.config(state=tk.DISABLED)
        
        # Aplicar filtro a la pestaña activa
        try:
            current_tab = self.module.notebook.index(self.module.notebook.select())
            
            if current_tab == 0:  # Pestaña "Todas"
                self.module.all_list.filter_data(search_text)
            elif current_tab == 1:  # Pestaña "Anticipos"
                self.module.advances_list.filter_data(search_text)
            elif current_tab == 2:  # Pestaña "Liquidaciones"
                self.module.liquidations_list.filter_data(search_text)
                
        except Exception as e:
            print(f"Error en búsqueda: {e}")
    
    def _clear_search(self):
        """Limpia el campo de búsqueda"""
        self.search_var.set("")
        self.search_entry.delete(0, tk.END)
        self._set_placeholder()  # Restaurar placeholder
        self.clear_search_btn.config(state=tk.DISABLED)
        self._on_search()  # Aplicar búsqueda vacía para mostrar todos los datos
    
    def _refresh_with_search(self):
        """Actualiza los datos manteniendo la búsqueda actual"""
        self.module.refresh_diets()
        # Re-aplicar la búsqueda después de refrescar
        self._on_search()
    
    def update_buttons_state(self, selected_item ):
        """Actualiza el estado de los botones según la dieta seleccionada"""
        if selected_item  is None:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.liquidate_btn.config(state=tk.DISABLED)
            return  
        
        if hasattr(selected_item, 'liquidation_number'):
            self.edit_btn.config(text="Editar Liquidación", state=tk.NORMAL)
            self.liquidate_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.NORMAL)
            self.edit_btn.config(command=self.module.edit_liquidation)
        else:
            self.edit_btn.config(text="Editar Dieta", state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)
        if hasattr(selected_item, 'status') and selected_item.status == "requested":
            self.liquidate_btn.config(state=tk.NORMAL)
        else:
            self.liquidate_btn.config(state=tk.DISABLED)
        self.edit_btn.config(command=self.module.edit_item)

    def refresh_counters(self):
        """Actualiza los contadores en la interfaz"""
        try:
            counters = self.module.get_counters_info()
            self.counters_label.config(
                text=f"Anticipos: {counters.total_advance_number} | Liquidaciones: {counters.total_liquidation_number}"
            )
        except Exception as e:
            print(f"ERROR refrescando contadores: {e}")
            self.counters_label.config(text="Anticipos: 0 | Liquidaciones: 0")