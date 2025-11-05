import tkinter as tk
from tkinter import ttk

class RequestUserForm(ttk.Frame):
    """Formulario para crear y editar usuarios solicitantes"""
    
    def __init__(self, parent, submit_callback, departments, **kwargs):
        super().__init__(parent, **kwargs)
        self.submit_callback = submit_callback
        self.departments = departments
        self.is_edit_mode = False
        self.current_user_id = None
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del formulario"""
        self.columnconfigure(1, weight=1)

        # Campos del formulario
        labels = ["Username:", "Nombre Completo:", "Email:", "CI:", "Departamento:"]
        self.entries = {}
        
        for i, label in enumerate(labels):
            ttk.Label(self, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=5)
            
            if label == "Departamento:":
                # Combobox para seleccionar departamento
                dept_combo = ttk.Combobox(self, values=[dept.name for dept in self.departments], 
                                         state="readonly")
                dept_combo.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                if self.departments:
                    dept_combo.set(self.departments[0].name)
                self.entries['department'] = dept_combo
            else:
                entry = ttk.Entry(self, width=30)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                field_name = label.lower().replace(' ', '_').replace(':', '')
                self.entries[field_name] = entry

        # Botón de enviar
        self.submit_btn = ttk.Button(self, text="Crear Solicitante", command=self._on_submit)
        self.submit_btn.grid(row=5, column=1, sticky=tk.E, pady=10)

    def _on_submit(self):
        """Maneja el envío del formulario"""
        data = self.get_data()
        self.submit_callback(data, self.is_edit_mode, self.current_user_id)

    def get_data(self):
        """Obtiene los datos del formulario"""
        department_name = self.entries['department'].get()
        department_id = next((dept.id for dept in self.departments if dept.name == department_name), None)
        
        return {
            'username': self.entries['username'].get(),
            'fullname': self.entries['nombre_completo'].get(),
            'email': self.entries['email'].get(),
            'ci': self.entries['ci'].get(),
            'department_id': department_id
        }

    def clear(self):
        """Limpia el formulario"""
        for key, entry in self.entries.items():
            if hasattr(entry, 'delete'):
                entry.delete(0, tk.END)
            elif key == 'department' and self.departments:
                entry.set(self.departments[0].name)
        
        self.is_edit_mode = False
        self.current_user_id = None
        self.submit_btn.config(text="Crear Solicitante")

    def set_edit_mode(self, user_id, username, fullname, email, ci, department_id):
        """Configura el formulario para modo edición"""
        self.is_edit_mode = True
        self.current_user_id = user_id
        
        self.entries['username'].delete(0, tk.END)
        self.entries['username'].insert(0, username)
        
        self.entries['nombre_completo'].delete(0, tk.END)
        self.entries['nombre_completo'].insert(0, fullname)
        
        self.entries['email'].delete(0, tk.END)
        self.entries['email'].insert(0, email)
        
        self.entries['ci'].delete(0, tk.END)
        self.entries['ci'].insert(0, ci)
        
        # Establecer departamento
        department = next((dept for dept in self.departments if dept.id == department_id), None)
        if department:
            self.entries['department'].set(department.name)
        
        self.submit_btn.config(text="Actualizar Solicitante")