import tkinter as tk
from tkinter import ttk
from core.entities.user import UserRole

class UserForm(ttk.Frame):
    """Formulario para crear y editar usuarios"""
    
    def __init__(self, parent, submit_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.submit_callback = submit_callback
        self.entries = {}
        self.is_edit_mode = False
        self.current_user_id = None
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del formulario"""
        self.columnconfigure(1, weight=1)

        # Campos del formulario
        labels = ["Username:", "Email:", "Password:", "Rol:"]
        
        for i, label in enumerate(labels):
            ttk.Label(self, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=5)
            
            if label == "Rol:":
                role_var = tk.StringVar(value=UserRole.USER.value)
                role_combo = ttk.Combobox(self, textvariable=role_var, 
                                        values=[role.value for role in UserRole], 
                                        state="readonly")
                role_combo.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                self.entries['role'] = role_combo
            else:
                entry = ttk.Entry(self, width=30)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                field_name = label.lower().replace(':', '')
                self.entries[field_name] = entry
                if field_name == 'password':
                    entry.config(show="*")

        # Botón de enviar
        self.submit_btn = ttk.Button(self, text="Crear Usuario", command=self._on_submit)
        self.submit_btn.grid(row=4, column=1, sticky=tk.E, pady=10)

    def _on_submit(self):
        """Maneja el envío del formulario"""
        data = self.get_data()
        self.submit_callback(data, self.is_edit_mode, self.current_user_id)

    def get_data(self):
        """Obtiene los datos del formulario"""
        return {
            'username': self.entries['username'].get(),
            'email': self.entries['email'].get(),
            'password': self.entries['password'].get(),
            'role': UserRole(self.entries['role'].get())
        }

    def clear(self):
        """Limpia el formulario"""
        for key, entry in self.entries.items():
            if hasattr(entry, 'delete'):
                entry.delete(0, tk.END)
            elif key == 'role':
                entry.set(UserRole.USER.value)
        
        self.is_edit_mode = False
        self.current_user_id = None
        self.submit_btn.config(text="Crear Usuario")

    def set_edit_mode(self, user_id, username, email, role):
        """Configura el formulario para modo edición"""
        self.is_edit_mode = True
        self.current_user_id = user_id
        
        self.entries['username'].delete(0, tk.END)
        self.entries['username'].insert(0, username)
        
        self.entries['email'].delete(0, tk.END)
        self.entries['email'].insert(0, email)
        
        self.entries['role'].set(role.value)
        
        # En modo edición, el campo de password es opcional
        self.entries['password'].delete(0, tk.END)
        self.entries['password'].config(show="")
        
        self.submit_btn.config(text="Actualizar Usuario")