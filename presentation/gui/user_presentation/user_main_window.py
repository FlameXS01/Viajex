import tkinter as tk
from tkinter import ttk
from application.services.user_service import UserService

from presentation.gui.utils.windows_utils import WindowUtils
from presentation.gui.user_presentation.widgets.user_list import UserList
from presentation.gui.user_presentation.widgets.user_actions import UserActions
from presentation.gui.user_presentation.dialogs.user_dialog import UserDialog
from presentation.gui.user_presentation.dialogs.change_password_dialog import ChangePasswordDialog
from presentation.gui.user_presentation.dialogs.change_role_dialog import ChangeRoleDialog
from presentation.gui.user_presentation.dialogs.confirm_dialog import ConfirmDialog

class UserMainWindow:
    """Ventana de gestión de usuarios - Ahora como módulo independiente"""
    
    def __init__(self, user_service: UserService, parent=None):
        self.user_service = user_service
        self.selected_user_id = None
        
        # Crear ventana hija si se proporciona parent, sino ventana principal
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Gestión de Usuarios")
        self.root.geometry("1000x700")
        
        # Centrar respecto al parent si existe
        if parent:
            WindowUtils.center_window(self.root, parent)
        else:
            WindowUtils.center_window(self.root)
        
        # Hacer responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self._setup_styles()
        self._create_widgets()
        self._load_users()

    def _setup_styles(self):
        """Configura estilos personalizados"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#f0f0f0')
        style.configure('Section.TLabelframe.Label', font=('Arial', 10, 'bold'))

    def _create_widgets(self):
        """Crea los widgets principales usando componentes modulares"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Gestión de Usuarios", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W+tk.E)
        
        # Botón para crear usuario
        create_button = ttk.Button(main_frame, text="Crear Nuevo Usuario", 
                                 command=self._create_user)
        create_button.grid(row=1, column=0, sticky=tk.W, pady=(0, 15))
        
        # Lista de usuarios (componente modular)
        list_frame = ttk.LabelFrame(main_frame, text="Usuarios Existentes", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.user_list = UserList(list_frame, self._on_user_select)
        self.user_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Acciones de usuario (componente modular)
        actions_frame = ttk.LabelFrame(main_frame, text="Acciones", padding="15")
        actions_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.user_actions = UserActions(actions_frame, {
            'edit': self._edit_user,
            'change_role': self._change_role,
            'change_password': self._change_password,
            'toggle_active': self._toggle_active,
            'delete': self._delete_user
        })
        self.user_actions.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
    def _on_user_select(self, user_id):
        """Maneja la selección de usuarios"""
        self.selected_user_id = user_id
        if user_id:
            self.user_actions.set_buttons_state(tk.NORMAL)
        else:
            self.user_actions.set_buttons_state(tk.DISABLED)

    def _create_user(self):
        """Abre diálogo para crear nuevo usuario"""
        dialog = UserDialog(self.root, self.user_service)
        result = dialog.show()
        if result:
            self._load_users()

    def _edit_user(self):
        """Abre diálogo para editar usuario existente"""
        if not self.selected_user_id:
            return
            
        user = self.user_service.get_user_by_id(self.selected_user_id)
        if user:
            dialog = UserDialog(self.root, self.user_service, user)
            result = dialog.show()
            if result:
                self._load_users()

    def _change_role(self):
        """Cambia el rol del usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        user = self.user_service.get_user_by_id(self.selected_user_id)
        if user:
            ChangeRoleDialog(self.root, self.user_service, self.selected_user_id, user.role)
            self._load_users()

    def _change_password(self):
        """Cambia la contraseña del usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        ChangePasswordDialog(self.root, self.user_service, self.selected_user_id)

    def _toggle_active(self):
        """Activa/desactiva el usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        try:
            user = self.user_service.toggle_user_active(self.selected_user_id)
            status = "activado" if user.is_active else "desactivado"
            from tkinter import messagebox
            messagebox.showinfo("Éxito", f"Usuario {status} correctamente")
            self._load_users()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo cambiar el estado: {str(e)}")

    def _delete_user(self):
        """Elimina el usuario seleccionado"""
        if not self.selected_user_id:
            return
            
        user = self.user_service.get_user_by_id(self.selected_user_id)
        if not user:
            from tkinter import messagebox
            messagebox.showerror("Error", "Usuario no encontrado")
            return
            
        def confirm_delete():
            try:
                success = self.user_service.delete_user(self.selected_user_id)
                if success:
                    from tkinter import messagebox
                    messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                    self.selected_user_id = None
                    self._load_users()
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Error", "No se pudo eliminar el usuario")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"No se pudo eliminar el usuario: {str(e)}")

        ConfirmDialog(
            self.root,
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar al usuario '{user.username}'?\nEsta acción no se puede deshacer.",
            confirm_delete
        )

    def _load_users(self):
        """Carga los usuarios en la lista"""
        try:
            users = self.user_service.get_all_users()
            self.user_list.load_users(users)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios: {str(e)}")

    def run(self):
        """Inicia la ventana (para uso independiente)"""
        self.root.mainloop()