import tkinter as tk
from tkinter import ttk, messagebox
from application.services.user_service import UserService

# Importar componentes modulares
from presentation.gui.user_presentation.widgets.user_list import UserList
from presentation.gui.user_presentation.widgets.user_actions import UserActions
from presentation.gui.user_presentation.dialogs.user_dialog import UserDialog
from presentation.gui.user_presentation.dialogs.change_password_dialog import ChangePasswordDialog
from presentation.gui.user_presentation.dialogs.change_role_dialog import ChangeRoleDialog
from presentation.gui.user_presentation.dialogs.confirm_dialog import ConfirmDialog

class UserModule(ttk.Frame):
    """Módulo de gestión de usuarios para embeber en el dashboard - VERSIÓN CORREGIDA"""
    
    def __init__(self, parent, user_service: UserService):
        super().__init__(parent, style='Content.TFrame')  # Asegurar estilo
        self.user_service = user_service
        self.selected_user_id = None
        
        self._create_widgets()
        self._load_users()

    def _create_widgets(self):
        """Crea la interfaz del módulo de usuarios"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header del módulo
        header_frame = ttk.Frame(self, style='Content.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(header_frame, text="Gestión de Usuarios", 
                 font=('Arial', 18, 'bold'), style='Content.TLabel').grid(row=0, column=0, sticky='w')
        
        # Botón de crear usuario
        create_btn = ttk.Button(header_frame, text="➕ Crear Usuario", 
                               command=self._create_user)
        create_btn.grid(row=0, column=1, sticky='e', padx=(0, 10))
        
        # Contenido principal (lista + acciones)
        content_frame = ttk.Frame(self, style='Content.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew')
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Lista de usuarios
        list_frame = ttk.LabelFrame(content_frame, text="Usuarios Registrados", padding="15")
        list_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.user_list = UserList(list_frame, self._on_user_select)
        self.user_list.grid(row=0, column=0, sticky='nsew')
        
        # Panel de acciones
        actions_frame = ttk.LabelFrame(content_frame, text="Acciones Disponibles", padding="15")
        actions_frame.grid(row=1, column=0, sticky='ew')
        
        self.user_actions = UserActions(actions_frame, {
            'edit': self._edit_user,
            'change_role': self._change_role,
            'change_password': self._change_password,
            'toggle_active': self._toggle_active,
            'delete': self._delete_user
        })
        self.user_actions.grid(row=0, column=0, sticky='ew')

    def _on_user_select(self, user_id):
        """Maneja la selección de usuarios en la lista"""
        self.selected_user_id = user_id
        if user_id:
            self.user_actions.set_buttons_state(tk.NORMAL)
        else:
            self.user_actions.set_buttons_state(tk.DISABLED)

    def _create_user(self):
        """Abre diálogo para crear nuevo usuario"""
        try:
            # Pasar self.winfo_toplevel() como parent para asegurar que sea modal
            dialog = UserDialog(self.winfo_toplevel(), self.user_service)
            result = dialog.show()
            if result:
                self._load_users()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el diálogo: {str(e)}")

    def _edit_user(self):
        """Abre diálogo para editar usuario existente"""
        if not self.selected_user_id:
            return
            
        try:
            user = self.user_service.get_user_by_id(self.selected_user_id)
            if user:
                dialog = UserDialog(self.winfo_toplevel(), self.user_service, user)
                result = dialog.show()
                if result:
                    self._load_users()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar el usuario: {str(e)}")

    def _change_role(self):
        """Cambia el rol del usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        try:
            user = self.user_service.get_user_by_id(self.selected_user_id)
            if user:
                ChangeRoleDialog(self.winfo_toplevel(), self.user_service, self.selected_user_id, user.role)
                self._load_users()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el rol: {str(e)}")

    def _change_password(self):
        """Cambia la contraseña del usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        try:
            ChangePasswordDialog(self.winfo_toplevel(), self.user_service, self.selected_user_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar la contraseña: {str(e)}")

    def _toggle_active(self):
        """Activa/desactiva el usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        try:
            user = self.user_service.toggle_user_active(self.selected_user_id)
            status = "activado" if user.is_active else "desactivado"
            messagebox.showinfo("Éxito", f"Usuario {status} correctamente")
            self._load_users()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el estado: {str(e)}")

    def _delete_user(self):
        """Elimina el usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        try:
            user = self.user_service.get_user_by_id(self.selected_user_id)
            if not user:
                messagebox.showerror("Error", "Usuario no encontrado")
                return
                
            def confirm_delete():
                try:
                    success = self.user_service.delete_user(self.selected_user_id)  # type: ignore
                    if success:
                        messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                        self.selected_user_id = None
                        self._load_users()
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar el usuario")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar el usuario: {str(e)}")

            ConfirmDialog(
                self.winfo_toplevel(),
                "Confirmar Eliminación",
                f"¿Estás seguro de que quieres eliminar al usuario '{user.username}'?\nEsta acción no se puede deshacer.",
                confirm_delete
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar usuario: {str(e)}")

    def _load_users(self):
        """Carga los usuarios en la lista"""
        try:
            users = self.user_service.get_all_users()
            self.user_list.load_users(users)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios: {str(e)}")