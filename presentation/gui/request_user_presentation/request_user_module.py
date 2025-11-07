import tkinter as tk
from tkinter import ttk, messagebox
from application.services.request_service import UserRequestService
from application.services.department_service import DepartmentService

# Importar componentes modulares
from presentation.gui.request_user_presentation.widgets.request_user_list import RequestUserList
from presentation.gui.request_user_presentation.widgets.request_user_actions import RequestUserActions
from presentation.gui.request_user_presentation.dialogs.request_user_dialog import RequestUserDialog
from presentation.gui.user_presentation.dialogs.confirm_dialog import ConfirmDialog

class RequestUserModule(ttk.Frame):
    """Módulo de gestión de usuarios solicitantes"""
    
    def __init__(self, parent, request_user_service: UserRequestService, department_service: DepartmentService):
        super().__init__(parent, style='Content.TFrame')
        self.request_user_service = request_user_service
        self.department_service = department_service
        self.selected_user_id = None
        
        self._create_widgets()
        self._load_users()

    def _create_widgets(self):
        """Crea los widgets principales usando componentes modulares"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self, style='Content.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="Gestión de Solicitantes", 
                 font=('Arial', 18, 'bold'), style='Content.TLabel').grid(row=0, column=0, sticky='w')
        
        ttk.Button(header_frame, text="➕ Crear Solicitante", 
                  command=self._create_user).grid(row=0, column=1, sticky='e')
        
        # Lista de usuarios (componente modular)
        list_frame = ttk.LabelFrame(self, text="Solicitantes Registrados", padding="15")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.user_list = RequestUserList(list_frame, self._on_user_select)
        self.user_list.grid(row=0, column=0, sticky='nsew')
        
        # Acciones de usuario (componente modular)
        actions_frame = ttk.LabelFrame(self, text="Acciones", padding="15")
        actions_frame.grid(row=2, column=0, sticky='ew')
        
        self.user_actions = RequestUserActions(actions_frame, {
            'edit': self._edit_user,
            'delete': self._delete_user
        })
        self.user_actions.grid(row=0, column=0, sticky='ew')

    def _on_user_select(self, user_id):
        """Maneja la selección de usuarios"""
        self.selected_user_id = user_id
        if user_id:
            self.user_actions.set_buttons_state(tk.NORMAL)
        else:
            self.user_actions.set_buttons_state(tk.DISABLED)

    def _create_user(self):
        """Abre diálogo para crear nuevo usuario"""
        dialog = RequestUserDialog(self.winfo_toplevel(), self.request_user_service, self.department_service)
        result = dialog.show()
        if result:
            self._load_users()

    def _edit_user(self):
        """Abre diálogo para editar usuario existente"""
        if not self.selected_user_id:
            return
            
        user = self.request_user_service.get_user_by_id(self.selected_user_id)
        if user:
            dialog = RequestUserDialog(self.winfo_toplevel(), self.request_user_service, self.department_service, user)
            result = dialog.show()
            if result:
                self._load_users()

    def _delete_user(self):
        """Elimina el usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        user = self.request_user_service.get_user_by_id(self.selected_user_id)
        if not user:
            messagebox.showerror("Error", "Solicitante no encontrado")
            return
            
        def confirm_delete():
            try:
                success = self.request_user_service.delete_user(self.selected_user_id)
                if success:
                    messagebox.showinfo("Éxito", "Solicitante eliminado correctamente")
                    self.selected_user_id = None
                    self._load_users()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el solicitante")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el solicitante: {str(e)}")

        ConfirmDialog(
            self.winfo_toplevel(),
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar al solicitante '{user.username}'?\nEsta acción no se puede deshacer.",
            confirm_delete
        )

    def _load_users(self):
        """Carga los usuarios en la lista"""
        try:
            users = self.request_user_service.get_all_users()
            
            # Enriquecer usuarios con nombres de departamentos
            enriched_users = []
            for user in users:
                department = self.department_service.get_department_by_id(user.department_id)
                user.department_name = department.name if department else "Desconocido"
                enriched_users.append(user)
            
            self.user_list.load_users(enriched_users)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los solicitantes: {str(e)}")