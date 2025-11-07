import tkinter as tk
from tkinter import ttk

class DepartmentForm(ttk.Frame):
    """Formulario para crear y editar departamentos"""
    
    def __init__(self, parent, submit_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.submit_callback = submit_callback
        self.is_edit_mode = False
        self.current_department_id = None
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del formulario"""
        self.columnconfigure(1, weight=1)

        # Campo de nombre
        ttk.Label(self, text="Nombre del Departamento:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=10)
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=10)

        # Botón de enviar
        self.submit_btn = ttk.Button(self, text="Crear Departamento", command=self._on_submit)
        self.submit_btn.grid(row=1, column=1, sticky=tk.E, pady=10)

    def _on_submit(self):
        """Maneja el envío del formulario"""
        name = self.name_entry.get()
        if name:
            self.submit_callback(name, self.is_edit_mode, self.current_department_id)

    def get_data(self):
        """Obtiene los datos del formulario"""
        return self.name_entry.get()

    def clear(self):
        """Limpia el formulario"""
        self.name_entry.delete(0, tk.END)
        self.is_edit_mode = False
        self.current_department_id = None
        self.submit_btn.config(text="Crear Departamento")

    def set_edit_mode(self, department_id, name):
        """Configura el formulario para modo edición"""
        self.is_edit_mode = True
        self.current_department_id = department_id
        
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.submit_btn.config(text="Actualizar Departamento")