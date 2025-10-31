import tkinter as tk
from tkinter import ttk
from core.entities.user import UserRole
from presentation.gui.utils.windows_utils import WindowUtils

class ChangeRoleDialog:
    """Diálogo para cambiar el rol de un usuario"""
    
    def __init__(self, parent, user_service, user_id, current_role):
        self.user_service = user_service
        self.user_id = user_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cambiar Rol")
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        WindowUtils.center_window(self.dialog, parent)
        self._create_widgets(current_role)

    def _create_widgets(self, current_role):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Selecciona el nuevo rol:").pack(pady=10)
        
        self.role_var = tk.StringVar(value=current_role.value)
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var, 
                                values=[role.value for role in UserRole], 
                                state="readonly")
        role_combo.pack(pady=5)

        ttk.Button(main_frame, text="Guardar", command=self._save).pack(pady=10)

    def _save(self):
        """Guarda el nuevo rol"""
        try:
            new_role = UserRole(self.role_var.get())
            self.user_service.update_user_role(self.user_id, new_role)
            self.dialog.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo actualizar el rol: {str(e)}")