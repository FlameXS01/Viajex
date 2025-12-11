from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.utils.windows_utils import WindowUtils
from presentation.gui.user_presentation.user_module import UserModule
from presentation.gui.card_presentation.card_module import CardModule
from presentation.gui.card_presentation.card_main_window import CardMainWindow

class MainDashboard:
    """Dashboard principal con navegación tipo SPA - VERSIÓN CORREGIDA"""
    
    def __init__(self, user, user_service, auth_service, department_service, 
                request_user_service, card_service, diet_service, settings_service=None, database_service=None
                ):
        self.user = user
        self.user_service = user_service
        self.auth_service = auth_service
        self.department_service = department_service
        self.card_service = card_service
        self.request_user_service = request_user_service
        self.diet_service = diet_service
        self.current_module_instance = None  
        self.settings_service = settings_service
        self.database_service = database_service

        if database_service is None:
            try:
                from infrastructure.database.database_service import DatabaseService
                self.database_service = DatabaseService("dietas_app.db")
            except Exception as e:
                print(f"❌ No se pudo crear DatabaseService: {e}")
                self.database_service = None
        else:
            self.database_service = database_service

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
        
        # Módulo de Departments (solo para admin/manager)
        if self.user.role.value in ['admin', 'manager', 'user']:
            dept_btn = ttk.Button(nav_frame, text="🏢 Gestión de Departamentos", 
                                style='Sidebar.TButton',
                                command=lambda: self._show_module('departments'))
            dept_btn.pack(fill=tk.X, pady=5)
            self.nav_buttons['departments'] = dept_btn

        # Módulo de Solicitantes
        request_btn = ttk.Button(nav_frame, text="👥 Gestión de Solicitantes", 
                            style='Sidebar.TButton',
                            command=lambda: self._show_module('request_users'))
        request_btn.pack(fill=tk.X, pady=5)
        self.nav_buttons['request_users'] = request_btn
        
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
        
        # Navbar superior elegante
        self.navbar_frame = ttk.Frame(self.content_frame, style='Content.TFrame', height=35)
        self.navbar_frame.pack(fill=tk.X)
        self.navbar_frame.pack_propagate(False)

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
        

        # Separador decorativo
        separator = ttk.Separator(self.navbar_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, side=tk.BOTTOM)

        # Opciones del navbar
        self._create_navbar_widgets()

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
            
            elif module_name == 'cards':  
                self.module_title.config(text="Gestión de Tarjetas")
                self.current_module_instance = CardModule(self.module_container, self.card_service)
                self.current_module_instance.pack(fill=tk.BOTH, expand=True)
                
            
            elif module_name == 'request_users':
                self.module_title.config(text="Gestión de Solicitantes")
                from presentation.gui.request_user_presentation.request_user_module import RequestUserModule
                self.current_module_instance = RequestUserModule(
                    self.module_container, 
                    self.request_user_service,
                    self.department_service
                )
                self.current_module_instance.pack(fill=tk.BOTH, expand=True)
                
            elif module_name == 'diets': 
                self.module_title.config(text="Gestión de Dietas")
                from presentation.gui.diet_presentation.diet_module import DietModule
                self.current_module_instance = DietModule(
                    self.module_container,
                    self.diet_service, 
                    self.request_user_service,
                    self.card_service
                )
                self.current_module_instance.pack(fill=tk.BOTH, expand=True)
                
            elif module_name == 'reports':
                self.module_title.config(text="Reportes y Estadísticas")
                placeholder = ttk.Frame(self.module_container, style='Content.TFrame')
                placeholder.pack(fill=tk.BOTH, expand=True)
                ttk.Label(placeholder, text="Módulo de Reportes - En desarrollo", 
                         font=('Arial', 16), style='Content.TLabel').pack(expand=True)
                
            elif module_name == 'departments':
                self.module_title.config(text="Gestión de Departamentos")
                from presentation.gui.department_presentation.department_module import DepartmentModule
                self.current_module_instance = DepartmentModule(self.module_container, self.department_service)
                self.current_module_instance.pack(fill=tk.BOTH, expand=True)
                                        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el módulo: {str(e)}")
            import traceback
            traceback.print_exc()  
            self._show_welcome_screen()

    def _update_nav_buttons(self, active_module):
        """Actualiza el estilo de los botones de navegación"""
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

    def _create_navbar_widgets(self):
        """Crea los widgets del navbar con menú de configuración"""
        
        # Menú Archivo
        file_btn = self._create_navbar_label("📁 Archivo")
        file_menu = tk.Menu(self.root, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self._new_file)
        file_menu.add_command(label="Abrir", command=self._open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self._on_close)
        self._bind_menu_to_label(file_btn, file_menu)
        
        # Menú Configuración
        config_btn = self._create_navbar_label("⚙️ Configuración")
        config_menu = tk.Menu(self.root, tearoff=0)

        # INICIAR CICLO
        config_menu.add_command(label="🔄 Iniciar Nuevo Ciclo", 
                          command=self._start_new_cycle,
                          foreground='#e74c3c',  
                          font=('Arial', 10, 'bold'))
    
        config_menu.add_separator()

        # Menú Ajustes Generales
        config_menu.add_command(label="Ajustes Generales", command=self._show_general_settings)
        config_menu.add_command(label="Parámetros del Sistema", command=self._show_system_params)
        config_menu.add_separator()

        
        # Submenú de apariencia
        appearance_menu = tk.Menu(config_menu, tearoff=0)
        appearance_menu.add_command(label="Tema Claro", command=lambda: self._change_theme("light"))
        appearance_menu.add_command(label="Tema Oscuro", command=lambda: self._change_theme("dark"))
        appearance_menu.add_command(label="Tema Azul", command=lambda: self._change_theme("blue"))
        config_menu.add_cascade(label="Apariencia", menu=appearance_menu)
        
        config_menu.add_separator()
        config_menu.add_command(label="Backup Base de Datos", command=self._backup_database)
        config_menu.add_command(label="Restaurar Backup", command=self._restore_backup)
        config_menu.add_command(label="Logs del Sistema", command=self._show_system_logs)
        
        self._bind_menu_to_label(config_btn, config_menu)

    def _create_navbar_label(self, text):
        """Crea una etiqueta clickeable para el navbar"""
        label = ttk.Label(
            self.navbar_frame, 
            text=text, 
            cursor="hand2",
            font=('Arial', 9), 
            padding=(15, 8), 
            style='Navbar.TLabel'
        )
        label.pack(side=tk.LEFT)
        label.bind('<Enter>', lambda e, l=label: l.configure(foreground='#3498db'))
        label.bind('<Leave>', lambda e, l=label: l.configure(foreground='black'))
        return label

    def _bind_menu_to_label(self, label, menu):
        """Vincula un menú a una etiqueta del navbar"""
        label.bind('<Button-1>', lambda e: self._show_menu_at_widget(menu, label))

    def _show_menu_at_widget(self, menu, widget):
        """Muestra un menú en la posición del widget"""
        try:
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _show_general_settings(self):
        """Muestra ventana de configuración general"""
        from presentation.gui.config_presentation.settings_window import SettingsWindow
        settings_window = SettingsWindow(
            self.root, 
            self.settings_service,
            self.database_service  
        )

    def _change_theme(self, theme):
        """Cambia el tema de la aplicación"""
        self._apply_theme(theme)
        if self.settings_service:
            settings = self.settings_service.get_settings()
            settings.theme = theme
            self.settings_service.save_settings(settings)
        
    def _apply_theme(self, theme):
        """Aplica un tema específico a la aplicación - VERSIÓN COMPLETA""" 
        style = ttk.Style()
        
        themes = {
            "light": {
                "bg": "#ecf0f1", 
                "sidebar": "#2c3e50",
                "text": "#2c3e50",
                "button_bg": "#3498db"
            },
            "dark": {
                "bg": "#2c3e50", 
                "sidebar": "#1a252f",
                "text": "#ecf0f1",
                "button_bg": "#34495e"
            },
            "blue": {
                "bg": "#e3f2fd", 
                "sidebar": "#1565c0",
                "text": "#0d47a1",
                "button_bg": "#1976d2"
            }
        }
        
        if theme in themes:
            colors = themes[theme]
            
            # Aplicar colores a los estilos
            style.configure('Content.TFrame', background=colors['bg'])
            style.configure('Content.TLabel', background=colors['bg'], 
                          foreground=colors['text'])
            style.configure('Title.TLabel', background=colors['bg'], 
                          foreground=colors['text'])
            style.configure('Welcome.TLabel', background=colors['bg'], 
                          foreground=colors['text'])
            
            # Sidebar
            style.configure('Sidebar.TFrame', background=colors['sidebar'])
            style.configure('Sidebar.TLabel', background=colors['sidebar'], 
                          foreground='white')
            
            # Botones del sidebar
            style.configure('Sidebar.TButton', background=colors['button_bg'])
            style.configure('Sidebar.Active.TButton', 
                          background=colors['button_bg'])
            
            # Navbar
            style.configure('Navbar.TLabel', background=colors['bg'], 
                          foreground=colors['text'])
            
            # Actualizar widgets existentes
            self.content_frame.configure(style='Content.TFrame')
            self.navbar_frame.configure(style='Content.TFrame')
            self.header_frame.configure(style='Content.TFrame')
            self.module_container.configure(style='Content.TFrame')
            
            messagebox.showinfo("Tema cambiado", 
                              f"Tema '{theme}' aplicado correctamente.\n\n"
                              "Los cambios se guardarán para la próxima sesión.")
            
    def _new_file(self):
        """Placeholder para Nuevo Archivo"""
        messagebox.showinfo("En desarrollo", 
                          "La función 'Nuevo Archivo' está en desarrollo.\n\n"
                          "Aquí podrás crear nuevos documentos o proyectos.")
        
    def _open_file(self):
        """Placeholder para Abrir Archivo"""
        messagebox.showinfo("En desarrollo", 
                          "La función 'Abrir Archivo' está en desarrollo.\n\n"
                          "Aquí podrás abrir documentos existentes.")
        
    def _show_system_params(self):
        """Placeholder para Parámetros del Sistema"""
        messagebox.showinfo("En desarrollo", 
                          "Los parámetros del sistema están en desarrollo.\n\n"
                          "Aquí podrás configurar:\n"
                          "- Límites de presupuesto\n"
                          "- Períodos de dieta\n"
                          "- Parámetros específicos del negocio")
       
    def _show_system_logs(self):
        """Placeholder para Mostrar Logs del Sistema"""
        # Crear ventana simple para logs
        log_window = tk.Toplevel(self.root)
        log_window.title("Logs del Sistema")
        log_window.geometry("600x400")
        log_window.transient(self.root)
        
        # Texto con scroll
        text_frame = ttk.Frame(log_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Agregar logs de ejemplo
        logs = [
            "2024-01-15 10:30:15 - Sistema iniciado",
            "2024-01-15 10:31:22 - Usuario 'admin' ha iniciado sesión",
            "2024-01-15 10:45:33 - Módulo de usuarios cargado",
            "2024-01-15 11:20:18 - Nuevo usuario creado: 'jperez'",
            "2024-01-15 12:15:45 - Backup automático completado",
            "2024-01-15 14:30:10 - Reporte generado exitosamente"
        ]
        
        for log in logs:
            text_widget.insert(tk.END, f"{log}\n")
        
        text_widget.config(state=tk.DISABLED)  
        
        # Botón para cerrar
        ttk.Button(log_window, text="Cerrar", 
                  command=log_window.destroy).pack(pady=10)
        
    def _backup_database(self):
        """Backup de base de datos desde el navbar"""
        if not self.database_service:
            messagebox.showerror("Error", "Servicio de base de datos no disponible 1")
            return
        
        # Crear backup rápido sin descripción
        try:
            backup_path = self.database_service.create_backup("")
            messagebox.showinfo(
                "Backup Rápido", 
                f"Backup creado exitosamente:\n{backup_path.name}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error creando backup: {str(e)}")

    def _restore_backup(self):
        """Abrir ventana de restauración"""
        from tkinter import filedialog
        import os
        
        initial_dir = "SalvasDietas" if os.path.exists("SalvasDietas") else "."
        
        backup_file = filedialog.askopenfilename(
            title="Seleccionar archivo de backup",
            initialdir=initial_dir,
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if backup_file:
            if not self.database_service:
                messagebox.showerror("Error", "Servicio de base de datos no disponible 2")
                return
            
            if messagebox.askyesno(
                "Confirmar Restauración",
                f"¿Restaurar desde:\n{os.path.basename(backup_file)}?\n\n"
                "Se creará un backup de la BD actual primero."
            ):
                try:
                    if self.database_service.restore_backup(Path(backup_file)):
                        messagebox.showinfo(
                            "Éxito", 
                            "Backup restaurado. Reinicie la aplicación."
                        )
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error restaurando: {str(e)}")

    def _start_new_cycle(self):
        """
        Inicia un nuevo ciclo: crea una nueva base de datos limpia
        sin dietas ni liquidaciones anteriores
        """
        if not self.database_service:
            messagebox.showerror("Error", "Servicio de base de datos no disponible")
            return
        
        # Mostrar ventana de confirmación
        confirm_text = """
        🆕 INICIAR NUEVO CICLO
        
        Esta acción creará una NUEVA base de datos que contendrá:

        ✅ SE CONSERVARÁ:
        • Solicitantes (requests)
        • Tarjetas (cards) 
        • Departamentos (department)
        • Usuarios del sistema (users)
        • Precios de servicios (diet_services)

        ❌ SE ELIMINARÁ POR COMPLETO:
        • Todas las dietas (diets)
        • Todas las liquidaciones (diet_liquidations)

        📝 NOTA SOBRE NUMERACIÓN:
        • Los nuevos anticipos comenzarán desde #1
        • Las nuevas liquidaciones comenzarán desde #1
        • (Tu sistema obtiene el máximo ID actual y suma 1)

        ¿Continuar?
        """
        
        if not messagebox.askyesno("Confirmar Nuevo Ciclo", confirm_text, icon='warning'):
            return
        
        # Pedir nombre para el nuevo ciclo
        from tkinter import simpledialog
        ciclo_nombre = simpledialog.askstring(
            "Nombre del Nuevo Ciclo",
            "Ingrese un nombre identificador para el nuevo ciclo:",
            initialvalue=f"Ciclo_{datetime.now().strftime('%Y_%m')}"
        )
        
        if not ciclo_nombre or ciclo_nombre.strip() == "":
            messagebox.showwarning("Nombre requerido", "Debe ingresar un nombre para el nuevo ciclo.")
            return
        
        # Crear backup automático (opcional pero recomendado)
        try:
            backup_path = self.database_service.create_backup(f"pre_ciclo_{ciclo_nombre}")
        except Exception as backup_error:
            if not messagebox.askyesno("Advertencia", 
                                    f"No se pudo crear el backup:\n{str(backup_error)}\n\n"
                                    "¿Continuar de todos modos?"):
                return
        
        # Mostrar progreso
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # Crear la nueva base de datos limpia
            new_db_path = self.database_service.create_clean_database_copy(ciclo_nombre)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "✅ Ciclo Creado",
                f"Nuevo ciclo '{ciclo_nombre}' creado exitosamente.\n\n"
                f"Ubicación: {new_db_path}\n\n"
                f"📊 Estado:\n"
                f"• Tablas de dietas: ELIMINADAS\n"
                f"• Tablas de liquidaciones: ELIMINADAS\n"
                f"• Datos maestros: CONSERVADOS\n\n"
                f"🎯 Próximos números:\n"
                f"• Próxima dieta: #1\n"
                f"• Próxima liquidación: #1"
            )
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo crear el nuevo ciclo:\n{str(e)}")
        
        finally:
            self.root.config(cursor="")

    def _show_post_cycle_options(self, new_db_path, ciclo_nombre):
        """Muestra opciones después de crear el nuevo ciclo"""
        
        # Crear ventana de opciones
        options_window = tk.Toplevel(self.root)
        options_window.title("Opciones del Nuevo Ciclo")
        options_window.geometry("500x400")
        options_window.transient(self.root)
        options_window.grab_set()
        
        # Centrar ventana
        options_window.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (options_window.winfo_width() // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (options_window.winfo_height() // 2)
        options_window.geometry(f"+{x}+{y}")
        
        # Título
        ttk.Label(options_window, text="🎯 Nuevo Ciclo Creado", 
                font=('Arial', 14, 'bold')).pack(pady=(20, 10))
        
        ttk.Label(options_window, 
                text=f"Ciclo: {ciclo_nombre}\nUbicación: {new_db_path.name}",
                wraplength=400).pack(pady=(0, 20))
        
        # Frame para opciones
        options_frame = ttk.Frame(options_window)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Opción 1: Usar ahora la nueva base de datos (requiere reinicio)
        def use_now():
            if messagebox.askyesno("Cambiar Base de Datos",
                                "Para usar la nueva base de datos, la aplicación debe reiniciarse.\n\n"
                                "¿Desea reiniciar ahora?"):
                # Guardar configuración para usar la nueva BD
                self._save_database_config(new_db_path)
                options_window.destroy()
                self.root.after(1000, self._restart_application)
        
        btn1 = ttk.Button(options_frame, text="🔄 Usar esta base de datos AHORA",
                        command=use_now, style='Accent.TButton')
        btn1.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="(Reiniciará la aplicación)", 
                font=('Arial', 8)).pack(pady=(0, 15))
        
        # Opción 2: Mantener la base de datos actual
        def keep_current():
            messagebox.showinfo("Base de Datos Actual",
                            "Se mantendrá la base de datos actual.\n"
                            "La nueva base de datos está disponible en:\n"
                            f"{new_db_path.parent}/")
            options_window.destroy()
        
        btn2 = ttk.Button(options_frame, text="📁 Mantener base de datos actual",
                        command=keep_current)
        btn2.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="(Puede cambiar manualmente después)", 
                font=('Arial', 8)).pack(pady=(0, 15))
        
        # Opción 3: Ver ubicación del archivo
        def show_location():
            import os
            os.startfile(new_db_path.parent)
            options_window.destroy()
        
        btn3 = ttk.Button(options_frame, text="📂 Abrir carpeta de ubicación",
                        command=show_location)
        btn3.pack(fill=tk.X, pady=5)
        
        # Separador
        ttk.Separator(options_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Opción 4: Cerrar
        ttk.Button(options_frame, text="Cerrar", 
                command=options_window.destroy).pack()

    def _save_database_config(self, db_path):
        """Guarda la configuración de la nueva base de datos"""
        config_path = Path("database_config.json")
        
        config = {
            'active_database': str(db_path),
            'previous_database': str(self.database_service.db_path),
            'changed_at': datetime.now().isoformat()
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _restart_application(self):
        """Reinicia la aplicación"""
        messagebox.showinfo("Reiniciar", 
                        "La aplicación se cerrará para completar el cambio.\n"
                        "Por favor, ábrala nuevamente manualmente.")
        self.root.quit()
        self.root.destroy()