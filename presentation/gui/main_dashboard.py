import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.utils.windows_utils import WindowUtils
from presentation.gui.user_presentation.user_module import UserModule
from presentation.gui.card_presentation.card_module import CardModule
from presentation.gui.card_presentation.card_main_window import CardMainWindow

class MainDashboard:
    """Dashboard principal con navegación tipo SPA - VERSIÓN CORREGIDA"""
    
    def __init__(self, user, user_service, auth_service, card_service):
        self.user = user
        self.user_service = user_service
        self.auth_service = auth_service
        self.current_module = None
        self.card_service = card_service
        self.current_module_instance = None  
        
        self.root = tk.Tk()
        self.root.title(f"Sistema de Gestión de Dietas - {user.username}")
        
        self.root.state('zoomed')
        self.root.minsize(1000, 600)
        
        # Configurar cierre seguro
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._setup_styles()
        self._create_widgets()
        self._show_welcome_screen()

    def _setup_styles(self):
        """Configura estilos modernos para la aplicación - VERSIÓN MEJORADA"""
        style = ttk.Style()
        
        # Configurar tema por defecto primero
        style.theme_use('clam')
        
        # Estilos para el sidebar
        style.configure('Sidebar.TFrame', background='#2c3e50')
        style.configure('Sidebar.TLabel', background='#2c3e50', foreground='white', font=('Arial', 12))
        
        # Botones del sidebar - ESTILOS CORREGIDOS
        style.configure('Sidebar.TButton', 
                       background='#34495e', 
                       foreground='white',
                       font=('Arial', 11),
                       padding=(15, 10),
                       anchor='w',
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Sidebar.TButton',
                 background=[('active', '#3498db'),
                           ('pressed', '#2980b9')])
        
        # Botón activo del sidebar
        style.configure('Sidebar.Active.TButton', 
                       background='#3498db', 
                       foreground='white',
                       font=('Arial', 11, 'bold'),
                       padding=(15, 10),
                       anchor='w',
                       borderwidth=0)
        
        # Estilos para el contenido
        style.configure('Content.TFrame', background='#ecf0f1')
        style.configure('Content.TLabel', background='#ecf0f1')
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'), background='#ecf0f1')
        style.configure('Welcome.TLabel', font=('Arial', 14), background='#ecf0f1')
        style.configure('Navbar.TLabel', font=('Arial', 10), background='#ecf0f1')
        style.map('Navbar.TLabel',
                foreground=[('active', '#3498db')])
        
    def _create_widgets(self):
        """Crea la interfaz con sidebar + área de contenido"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (Navegación lateral)
        self._create_sidebar(main_frame)
        
        # Área de contenido principal
        self._create_content_area(main_frame)

    def _create_sidebar(self, parent):
        """Crea la barra lateral de navegación - VERSIÓN MEJORADA"""
        sidebar_frame = ttk.Frame(parent, style='Sidebar.TFrame', width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)
        
        # Logo/Título de la app
        title_frame = ttk.Frame(sidebar_frame, style='Sidebar.TFrame')
        title_frame.pack(fill=tk.X, pady=(20, 10), padx=10)
        
        ttk.Label(title_frame, text="🥗 Dietas App", 
                 style='Sidebar.TLabel', font=('Arial', 16, 'bold')).pack()
        
        # Información del usuario
        user_frame = ttk.Frame(sidebar_frame, style='Sidebar.TFrame')
        user_frame.pack(fill=tk.X, pady=(0, 20), padx=15)
        
        ttk.Label(user_frame, text=f"👤 {self.user.username}", 
                 style='Sidebar.TLabel').pack(anchor='w')
        ttk.Label(user_frame, text=f"🎭 {self.user.role.value}", 
                 style='Sidebar.TLabel', font=('Arial', 10)).pack(anchor='w')
        
        # Separador
        separator = ttk.Separator(sidebar_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=10, padx=15)
        
        # Botones de navegación (Módulos)
        nav_frame = ttk.Frame(sidebar_frame, style='Sidebar.TFrame')
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Diccionario para mantener referencia a los botones
        self.nav_buttons = {}
        
        # Módulo de Usuarios (solo para admin/manager)
        if self.user.role.value in ['admin', 'manager']:
            btn = ttk.Button(nav_frame, text="👥 Gestión de Usuarios", 
                           style='Sidebar.TButton',
                           command=lambda: self._show_module('users'))
            btn.pack(fill=tk.X, pady=5)
            self.nav_buttons['users'] = btn
            
        # Módulo de Solicitantes 
        btn = ttk.Button(nav_frame, text="👤 Gestión de Solicitantes", 
                        style='Sidebar.TButton',
                        command=lambda: self._show_module('request'))
        btn.pack(fill=tk.X, pady=5)
        self.nav_buttons['request'] = btn
        
        # Módulo de Tarjetas
        btn = ttk.Button(nav_frame, text="💳 Gestión de Tarjetas", 
                        style='Sidebar.TButton',
                        command=lambda: self._show_module('cards'))
        btn.pack(fill=tk.X, pady=5)
        self.nav_buttons['cards'] = btn
        
        # Módulo de Dietas
        btn = ttk.Button(nav_frame, text="🥦 Gestión de Dietas", 
                       style='Sidebar.TButton',
                       command=lambda: self._show_module('diets'))
        btn.pack(fill=tk.X, pady=5)
        self.nav_buttons['diets'] = btn
        
        # Módulo de Reportes (solo para admin/manager)
        if self.user.role.value in ['admin', 'manager']:
            btn = ttk.Button(nav_frame, text="📊 Reportes y Estadísticas", 
                           style='Sidebar.TButton',
                           command=lambda: self._show_module('reports'))
            btn.pack(fill=tk.X, pady=5)
            self.nav_buttons['reports'] = btn
        
        # Espacio flexible
        ttk.Frame(nav_frame, style='Sidebar.TFrame').pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción en la parte inferior
        action_frame = ttk.Frame(sidebar_frame, style='Sidebar.TFrame')
        action_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20, padx=10)
        
        ttk.Button(action_frame, text="🚪 Cerrar Sesión", 
                  style='Sidebar.TButton',
                  command=self._logout).pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="⛌ Salir", 
                  style='Sidebar.TButton',
                  command=self._on_close).pack(fill=tk.X, pady=5)

    def _create_content_area(self, parent):
        """Crea el área de contenido principal"""
        self.content_frame = ttk.Frame(parent, style='Content.TFrame')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header del contenido
        self.header_frame = ttk.Frame(self.content_frame, style='Content.TFrame', height=80)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)
        
        # Título del módulo actual
        self.module_title = ttk.Label(self.header_frame, text="Bienvenido", 
                                     style='Title.TLabel')
        self.module_title.pack(side=tk.LEFT, padx=30, pady=20)
        
        # Área donde se renderizarán los módulos
        self.module_container = ttk.Frame(self.content_frame, style='Content.TFrame')
        self.module_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        
        # Navbar superior elegante
        self.navbar_frame = ttk.Frame(self.content_frame, style='Content.TFrame', height=35)
        self.navbar_frame.pack(fill=tk.X)
        self.navbar_frame.pack_propagate(False)

        # Separador decorativo
        separator = ttk.Separator(self.navbar_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, side=tk.BOTTOM)

        # Opciones del navbar
        navbar_options = [
            ("📁 Archivo", None),
            ("✏️ Editar", None), 
            ("👁️ Ver", None),
            ("🛠️ Herramientas", None),
            ("❓ Ayuda", None)
        ]

        for option, command in navbar_options:
            btn = ttk.Label(self.navbar_frame, text=option, cursor="hand2", 
                        font=('Arial', 9), padding=(15, 8), style='Navbar.TLabel')
            btn.pack(side=tk.LEFT)
            # Efecto hover básico
            btn.bind('<Enter>', lambda e, b=btn: b.configure(foreground='#3498db'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(foreground='black'))

    def _show_welcome_screen(self):
        """Muestra la pantalla de bienvenida"""
        self._clear_module_container()
        self.module_title.config(text="Bienvenido")
        self._update_nav_buttons(None)  # Ningún botón activo
        
        welcome_frame = ttk.Frame(self.module_container, style='Content.TFrame')
        welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje de bienvenida centrado
        center_frame = ttk.Frame(welcome_frame, style='Content.TFrame')
        center_frame.place(relx=0.5, rely=0.4, anchor='center')
        
        ttk.Label(center_frame, text="¡Bienvenido al Sistema de Gestión de Dietas!", 
                 style='Title.TLabel').pack(pady=10)
        
        ttk.Label(center_frame, 
                 text=f"Hola {self.user.username}, selecciona un módulo del menú lateral para comenzar.",
                 style='Welcome.TLabel').pack(pady=5)
        
        # Estadísticas rápidas
        stats_frame = ttk.Frame(welcome_frame, style='Content.TFrame')
        stats_frame.place(relx=0.5, rely=0.6, anchor='center')
        
        ttk.Label(stats_frame, text="Sistema listo para usar", 
                 style='Welcome.TLabel', foreground='gray').pack()

    def _show_module(self, module_name):
        """Muestra un módulo específico en el área de contenido - VERSIÓN CORREGIDA"""
        # Limpiar módulo anterior si existe
        if self.current_module_instance:
            self.current_module_instance.destroy()
            self.current_module_instance = None
        
        # Actualizar estado de botones de navegación
        self._update_nav_buttons(module_name)
        
        # Limpiar contenedor actual
        self._clear_module_container()
        
        # Cargar y mostrar el módulo solicitado
        try:
            if module_name == 'users':
                self.module_title.config(text="Gestión de Usuarios")
                self.current_module_instance = UserModule(self.module_container, self.user_service)
                self.current_module_instance.pack(fill=tk.BOTH, expand=True)
                
            elif module_name == 'patients':
                self.module_title.config(text="Gestión de Pacientes")
                placeholder = ttk.Frame(self.module_container, style='Content.TFrame')
                placeholder.pack(fill=tk.BOTH, expand=True)
                ttk.Label(placeholder, text="Módulo de Gestión de Pacientes - En desarrollo", 
                         font=('Arial', 16), style='Content.TLabel').pack(expand=True)
            
            elif module_name == 'cards':  
                self.module_title.config(text="Gestión de Tarjetas")
                self.current_module_instance = CardModule(self.module_container, self.card_service)
                self.current_module_instance.pack(fill=tk.BOTH, expand=True)
                
            
            elif module_name == 'request':
                self.module_title.config(text="Gestión de Solicitantes")
                placeholder = ttk.Frame(self.module_container, style='Content.TFrame')
                placeholder.pack(fill=tk.BOTH, expand=True)
                ttk.Label(placeholder, text="Módulo de Gestión de Solicitantes - En desarrollo", 
                         font=('Arial', 16), style='Content.TLabel').pack(expand=True)
                
            elif module_name == 'diets':
                self.module_title.config(text="Gestión de Dietas")
                placeholder = ttk.Frame(self.module_container, style='Content.TFrame')
                placeholder.pack(fill=tk.BOTH, expand=True)
                ttk.Label(placeholder, text="Módulo de Gestión de Dietas - En desarrollo", 
                         font=('Arial', 16), style='Content.TLabel').pack(expand=True)
                
            elif module_name == 'reports':
                self.module_title.config(text="Reportes y Estadísticas")
                placeholder = ttk.Frame(self.module_container, style='Content.TFrame')
                placeholder.pack(fill=tk.BOTH, expand=True)
                ttk.Label(placeholder, text="Módulo de Reportes - En desarrollo", 
                         font=('Arial', 16), style='Content.TLabel').pack(expand=True)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo: {str(e)}")
            import traceback
            traceback.print_exc()  # Para debug
            self._show_welcome_screen()

    def _update_nav_buttons(self, active_module):
        """Actualiza el estilo de los botones de navegación - VERSIÓN MEJORADA"""
        for module_name, button in self.nav_buttons.items():
            if module_name == active_module:
                button.configure(style='Sidebar.Active.TButton')
            else:
                button.configure(style='Sidebar.TButton')

    def _clear_module_container(self):
        """Limpia el contenedor de módulos de forma segura"""
        for widget in self.module_container.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                # Ignorar errores de widgets ya destruidos
                pass

    def _logout(self):
        """Cierra sesión y vuelve al login"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de que quiere cerrar sesión?"):
            self.auth_service.logout()
            self.root.destroy()

    def _on_close(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askyesno("Salir", "¿Está seguro de que quiere salir de la aplicación?"):
            self.auth_service.logout()
            self.root.destroy()
            exit(0)

    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()