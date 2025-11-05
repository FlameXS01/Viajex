import tkinter as tk
from tkinter import ttk, messagebox
from application.dtos.request_user_dtos import RequestUserCreateDTO
from application.services.request_service import UserRequestService
from presentation.gui.utils.windows_utils import WindowUtils

class RequestUserDialog:
    """Diálogo para crear/editar usuarios solicitantes"""
    
    def __init__(self, parent, request_user_service: UserRequestService, department_service, user_data=None):
        self.request_user_service = request_user_service
        self.department_service = department_service
        self.user_data = user_data
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Solicitante" if user_data else "Crear Solicitante")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        WindowUtils.center_window(self.dialog, parent)
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Obtener departamentos para el combobox
        departments = self.department_service.get_all_departments()

        # Campos del formulario
        labels = ["Username:", "Nombre Completo:", "Email:", "CI:", "Departamento:"]
        self.entries = {}
        
        for i, label in enumerate(labels):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if label == "Departamento:":
                dept_names = [dept.name for dept in departments]
                dept_combo = ttk.Combobox(main_frame, values=dept_names, state="readonly")
                dept_combo.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                if dept_names:
                    dept_combo.set(dept_names[0])
                self.entries['department'] = dept_combo
            else:
                entry = ttk.Entry(main_frame, width=30)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
                field_name = label.lower().replace(' ', '_').replace(':', '')
                self.entries[field_name] = entry

        if self.user_data:
            def safe_insert(field_name, value):
                if value is None:
                    self.entries[field_name].insert(0, '')
                else:
                    self.entries[field_name].insert(0, str(value))
            
            safe_insert('username', self.user_data.username)
            safe_insert('nombre_completo', self.user_data.fullname)
            safe_insert('email', self.user_data.email)
            safe_insert('ci', self.user_data.ci)
            
            department = self.department_service.get_department_by_id(self.user_data.department_id)
            if department:
                self.entries['department'].set(department.name)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Guardar", command=self._save).grid(row=0, column=1, padx=5)

    def _save(self):
        """Guarda los datos del usuario solicitante"""
        username = self.entries['username'].get()
        fullname = self.entries['nombre_completo'].get()
        email = self.entries['email'].get()
        ci = self.entries['ci'].get()
        department_name = self.entries['department'].get()

        if not all([username, fullname, email, ci, department_name]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return

        try:
            # Obtener ID del departamento seleccionado
            departments = self.department_service.get_all_departments()
            department = next((dept for dept in departments if dept.name == department_name), None)

            user_data = RequestUserCreateDTO(
                    ci=ci,
                    username=username,
                    fullname=fullname,
                    email=email,
                    department_id=department.id
                )
            
            if not department:
                messagebox.showerror("Error", "Departamento no válido")
                return

            if self.user_data:
                # Actualizar usuario existente
                user = self.request_user_service.update_user(
                    self.user_data.id, username, email, fullname, department.id
                )
                self.result = user
                messagebox.showinfo("Éxito", "Solicitante actualizado correctamente")
            else:
                # Crear nuevo usuario
                user = self.request_user_service.create_user(user_data)
                self.result = user
                messagebox.showinfo("Éxito", "Solicitante creado correctamente")
            
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el solicitante: {str(e)}")
       

    def show(self):
        """Muestra el diálogo y retorna el resultado"""
        self.dialog.wait_window()
        return self.result