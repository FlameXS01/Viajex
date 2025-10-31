import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.utils.windows_utils import WindowUtils

class ChangePasswordDialog:
    """Diálogo seguro para cambiar contraseñas"""
    
    def __init__(self, parent, user_service, user_id):
        self.user_service = user_service
        self.user_id = user_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cambiar Contraseña - Verificación de Seguridad")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        WindowUtils.center_window(self.dialog, parent)
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Contraseña actual
        ttk.Label(main_frame, text="Contraseña actual:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.current_password = ttk.Entry(main_frame, show="*", width=30)
        self.current_password.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.current_password.focus()

        # Nueva contraseña
        ttk.Label(main_frame, text="Nueva contraseña:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_password = ttk.Entry(main_frame, show="*", width=30)
        self.new_password.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Confirmar nueva contraseña
        ttk.Label(main_frame, text="Confirmar nueva contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_password = ttk.Entry(main_frame, show="*", width=30)
        self.confirm_password.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=10)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(button_frame, text="Guardar", command=self._save).grid(row=0, column=0, pady=5)

    def _save(self):
        """Guarda la nueva contraseña con validaciones de seguridad"""
        current = self.current_password.get()
        new = self.new_password.get()
        confirm = self.confirm_password.get()

        # Validaciones
        if not current:
            messagebox.showwarning("Advertencia", "Debe ingresar la contraseña actual")
            return
            
        if not new:
            messagebox.showwarning("Advertencia", "La nueva contraseña no puede estar vacía")
            return
            
        if new != confirm:
            messagebox.showwarning("Advertencia", "Las nuevas contraseñas no coinciden")
            return
            
        if len(new) < 6:
            messagebox.showwarning("Advertencia", "La nueva contraseña debe tener al menos 8 caracteres")
            return

        try:
            self.user_service.update_user_password(self.user_id, current, new)
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Error de Seguridad", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la contraseña: {str(e)}")