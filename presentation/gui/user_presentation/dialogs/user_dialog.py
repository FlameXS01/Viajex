import tkinter as tk
from tkinter import ttk, messagebox
from core.entities.user import UserRole
from presentation.gui.utils.windows_utils import WindowUtils

class UserDialog:
    """Diálogo para crear/editar usuarios - VERSIÓN CORREGIDA"""
    
    def __init__(self, parent, user_service, user_data=None):
        self.user_service = user_service
        self.user_data = user_data
        self.result = None
        
        # Usar Toplevel correctamente
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Usuario" if user_data else "Crear Usuario")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Ajustar tamaño
        if user_data:
            self.dialog.geometry("400x300")
        else:
            self.dialog.geometry("400x400")
        
        # Evitar que el diálogo sea demasiado pequeño
        self.dialog.minsize(400, 300 if user_data else 400)
        
        WindowUtils.center_window(self.dialog, parent)
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del diálogo - VERSIÓN CORREGIDA"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        row = 0

        # Campos del formulario
        ttk.Label(main_frame, text="Username:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        row += 1

        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=30)
        self.email_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        row += 1

        ttk.Label(main_frame, text="Rol:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.role_combo = ttk.Combobox(main_frame, values=[role.value for role in UserRole], state="readonly")
        self.role_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.role_combo.set(UserRole.USER.value)
        row += 1

        # Solo mostrar campos de contraseña en modo creación
        if not self.user_data:
            ttk.Label(main_frame, text="Contraseña:").grid(row=row, column=0, sticky=tk.W, pady=5)
            self.password_entry = ttk.Entry(main_frame, width=30, show="*")
            self.password_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            row += 1

            ttk.Label(main_frame, text="Confirmar Contraseña:").grid(row=row, column=0, sticky=tk.W, pady=5)
            self.confirm_password_entry = ttk.Entry(main_frame, width=30, show="*")
            self.confirm_password_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            row += 1

        # Si estamos en modo edición, cargar los datos existentes
        if self.user_data:
            self.username_entry.insert(0, self.user_data.username)
            self.email_entry.insert(0, self.user_data.email)
            self.role_combo.set(self.user_data.role.value)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Guardar", command=self._save).grid(row=0, column=1, padx=5)

    def _save(self):
        """Guarda los datos del usuario - VERSIÓN CORREGIDA"""
        username = self.username_entry.get()
        email = self.email_entry.get()
        role = UserRole(self.role_combo.get())

        if not all([username, email]):
            messagebox.showwarning("Advertencia", "Username y Email son obligatorios")
            return

        try:
            if self.user_data:
                # Actualizar usuario existente
                user = self.user_data
                user.username = username
                user.email = email
                user.role = role
                
                # Usar el servicio para actualizar
                updated_user = self.user_service.update_user(user.id, username, email, role)
                self.result = updated_user
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            else:
                # Crear nuevo usuario
                password = self.password_entry.get()
                confirm_password = self.confirm_password_entry.get()
                
                if not password:
                    messagebox.showwarning("Advertencia", "La contraseña es obligatoria")
                    return
                    
                if password != confirm_password:
                    messagebox.showwarning("Advertencia", "Las contraseñas no coinciden")
                    return
                
                # Crear nuevo usuario usando el servicio
                new_user = self.user_service.create_user(username, email, password, role)
                self.result = new_user
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
            
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el usuario: {str(e)}")

    def show(self):
        """Muestra el diálogo y retorna el resultado"""
        self.dialog.wait_window()
        return self.result