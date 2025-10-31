import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.utils.windows_utils import WindowUtils

class LoginWindow:
    """Ventana de login para la aplicación"""
    
    def __init__(self, auth_service, on_login_success):
        self.auth_service = auth_service
        self.on_login_success = on_login_success
        
        self.root = tk.Tk()
        self.root.title("Login - Sistema de Dietas")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centrar ventana
        WindowUtils.center_window(self.root)
        
        # Evitar que se cierre con la X
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets de la ventana de login"""
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(main_frame, text="Sistema de Gestión de Dietas", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 30))

        # Campo de usuario
        ttk.Label(main_frame, text="Usuario:").pack(anchor=tk.W, pady=(10, 5))
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        self.username_entry.focus()

        # Campo de contraseña
        ttk.Label(main_frame, text="Contraseña:").pack(anchor=tk.W, pady=(5, 5))
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 20))

        # Botón de login
        login_button = ttk.Button(main_frame, text="Iniciar Sesión", command=self._login)
        login_button.pack(fill=tk.X, pady=(0, 10))

        # Información de credenciales por defecto
        info_label = ttk.Label(main_frame, text="Usuario: admin | Contraseña: admin01*", 
                              font=('Arial', 8), foreground='gray')
        info_label.pack(pady=(10, 0))

        # Bind Enter para login
        self.root.bind('<Return>', lambda event: self._login())

    def _login(self):
        """Maneja el intento de login"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Advertencia", "Por favor ingrese usuario y contraseña")
            return

        try:
            session = self.auth_service.login(username, password)
            messagebox.showinfo("Éxito", f"Bienvenido, {session.user.username}!")
            self.root.destroy()
            self.on_login_success(session.user)
        except Exception as e:
            messagebox.showerror("Error de Autenticación", str(e))

    def _on_close(self):
        """Maneja el cierre de la ventana"""
        if messagebox.askokcancel("Salir", "¿Está seguro de que quiere salir?"):
            self.root.destroy()
            exit(0)

    def run(self):
        """Inicia la ventana de login"""
        self.root.mainloop()