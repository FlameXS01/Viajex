from datetime import datetime
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from application.dtos.diet_dtos import DietServiceCreateDTO
from application.dtos.request_user_dtos import RequestUserCreateDTO
from core.entities.user import UserRole
from presentation.gui.user_presentation.user_module import UserModule
from presentation.gui.card_presentation.card_module import CardModule
from tkinter import filedialog, messagebox
import pandas as pd
from presentation.gui.utils.progress_dialog import show_progress_dialog, ProgressDialog

class MainDashboard:
    """Dashboard principal con navegación tipo SPA - VERSIÓN CORREGIDA"""
    
    def __init__(self, user, user_service, auth_service, department_service, 
                request_user_service, card_service, diet_service, account_service, card_transaction_service, settings_service=None, database_service=None
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
        self.account_service = account_service
        self.card_transaction_service = card_transaction_service

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
                self.current_module_instance = CardModule(self.module_container, self.card_service, self.card_transaction_service)
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
                    self.card_service,
                    self.department_service
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

        file_menu.add_command(
                label="📊 Manejar Cuentas", 
                command=self._manage_accounts,
                accelerator="Ctrl+A"
            )

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

        # Submenú de Inicialización 
        init_menu = tk.Menu(config_menu, tearoff=0)
        init_menu.add_command(label="📂 Departamentos desde Excel", 
                            command=self._initialize_departments_from_file,
                            font=('Arial', 9))
        init_menu.add_command(label="👥 Solicitantes desde Excel", 
                            command=self._initialize_request_users_from_file,
                            font=('Arial', 9))
        init_menu.add_command(label="💳 Tarjetas desde Excel", 
                            command=self._initialize_cards_from_file,
                            font=('Arial', 9))
        init_menu.add_separator()
        init_menu.add_command(label="🍽️ Servicios de Dieta", 
                            command=self._initialize_diet_services,
                            font=('Arial', 9))
        init_menu.add_command(label="👨‍💼 Usuario Admin", 
                            command=self._initialize_admin_user,
                            font=('Arial', 9))
        init_menu.add_separator()
        init_menu.add_command(label="⚡ Inicializar Todo", 
                            command=self._initialize_all_from_files,
                            font=('Arial', 9, 'bold'),
                            foreground='#27ae60')
        config_menu.add_cascade(label="🔄 Inicialización", menu=init_menu)
        
        config_menu.add_separator()
        config_menu.add_command(label="💾 Backup Base de Datos", command=self._backup_database)
        config_menu.add_command(label="📥 Restaurar Backup", command=self._restore_backup)
        config_menu.add_command(label="📋 Logs del Sistema", command=self._show_system_logs)
        
        self._bind_menu_to_label(config_btn, config_menu)

        help_btn = self._create_navbar_label("❓ Ayuda")
        help_menu = tk.Menu(self.root, tearoff=0)
        
        help_menu.add_command(label="📖 Manual de Usuario", 
                            command=self._show_user_manual,
                            font=('Arial', 10))
        
        help_menu.add_command(label="📚 Documentación", 
                            command=self._show_documentation)
        
        help_menu.add_separator()
        
        help_menu.add_command(label="🛠️ Soporte Técnico", 
                            command=self._show_support_info,
                            font=('Arial', 10))
        
        self._bind_menu_to_label(help_btn, help_menu)

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

    def _start_new_cycle(self):
        """
        Inicia un nuevo ciclo desde el navbar (versión simplificada)
        """
        from tkinter import simpledialog
        
        if not self.database_service:
            messagebox.showerror("Error", "Servicio de base de datos no disponible")
            return
        
        # Pedir nombre del ciclo
        ciclo_nombre = simpledialog.askstring(
            "Nuevo Ciclo",
            "Ingrese nombre para el nuevo ciclo:",
            initialvalue=f"Ciclo_{datetime.now().strftime('%Y_%m')}",
            parent=self.root
        )
        
        if not ciclo_nombre:
            return
        
        # Mostrar confirmación
        if not messagebox.askyesno(
            "Confirmar Nuevo Ciclo",
            f"¿Crear nuevo ciclo '{ciclo_nombre}'?\n\n"
            "Esto creará un backup automático y cerrará la aplicación.",
            icon='warning'
        ):
            return
        
        # Bloquear interfaz
        self.root.config(cursor="watch")
        self.root.update()
        
        try:
            # El servicio ahora maneja todo automáticamente
            new_db_path = self.database_service.create_clean_database_copy(ciclo_nombre)
            
            # Mostrar mensaje final
            messagebox.showinfo(
                "✅ Ciclo Creado",
                f"Nuevo ciclo '{ciclo_nombre}' creado.\n\n"
                f"La aplicación se cerrará ahora.\n"
                f"Por favor, ábrala nuevamente."
            )
            
            # Forzar cierre
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo crear el ciclo:\n{str(e)}")
        finally:
            self.root.config(cursor="")
            self.auth_service.logout()
            self.root.destroy()
            exit(0)

    def _restore_backup(self):
        """
        Restaura backup desde el navbar (versión mejorada)
        """
        from tkinter import filedialog
        import os
        
        if not self.database_service:
            messagebox.showerror("Error", "Servicio de base de datos no disponible")
            return
        
        # Buscar en carpeta de backups por defecto
        initial_dir = "SalvasDietas" if os.path.exists("SalvasDietas") else "."
        
        backup_file = filedialog.askopenfilename(
            title="📂 Seleccionar archivo de backup",
            initialdir=initial_dir,
            filetypes=[
                ("Archivos de base de datos", "*.db"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not backup_file:
            return
        
        backup_path = Path(backup_file)
        
        # Confirmar
        if not messagebox.askyesno(
            "⚠️ Confirmar Restauración",
            f"¿Restaurar desde:\n{backup_path.name}?\n\n"
            f"ADVERTENCIA:\n"
            f"1. Se creará backup de la BD actual\n"
            f"2. La aplicación se CERRARÁ\n"
            f"3. Debe reiniciar manualmente"
        ):
            return
        
        try:
            # Bloquear interfaz
            self.root.config(cursor="watch")
            self.root.update()
            
            # Restaurar
            success = self.database_service.restore_backup(backup_path)
            
            if success:
                messagebox.showinfo(
                    "✅ Restauración Exitosa",
                    f"Backup restaurado.\n\n"
                    f"La aplicación se cerrará ahora.\n"
                    f"Por favor, ábrala nuevamente."
                )
                
                # Cerrar aplicación
                self.root.quit()
            else:
                messagebox.showerror("❌ Error", "No se pudo restaurar el backup")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error restaurando:\n{str(e)}")
        finally:
            self.root.config(cursor="")
            self.auth_service.logout()
            self.root.destroy()
            exit(0)

    def _run_with_progress(self, task_name: str, task_func, *args, **kwargs):
        """
        Ejecuta una tarea con diálogo de progreso
        """
        try:
            result = show_progress_dialog(
                self.root,
                task_func,
                task_name
            )
            return result
        except Exception as e:
            messagebox.showerror(f"❌ Error en {task_name}", f"{str(e)}")
            return None

    def _execute_departments_initialization(self, update_progress):
        """Lógica interna para inicializar departamentos con progreso"""
        from tkinter import filedialog
        import pandas as pd
        import os
        
        update_progress(0, "Seleccionando archivo...")
        
        file_path = filedialog.askopenfilename(
            title="📂 Seleccionar archivo Excel para departamentos",
            initialdir=".",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not file_path:
            return None
        
        update_progress(10, "Verificando archivo...")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo no existe: {file_path}")
        
        update_progress(20, "Leyendo archivo Excel...")
        
        df = pd.read_excel(file_path, skiprows=3)
        
        required_columns = ['Unidad']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Columnas faltantes: {', '.join(missing_columns)}")
        
        update_progress(30, "Procesando unidades...")
        
        # CORRECCIÓN: Usar value_counts() correctamente
        dirty_unidades = df['Unidad'].value_counts()
        unidades = []
        total_unidades = len(dirty_unidades)
        
        # CORRECCIÓN: Iterar sobre los índices (nombres de unidades)
        for idx, unidad in enumerate(dirty_unidades.index, 1):
            unidad_limpia = str(unidad).strip()
            if unidad_limpia and unidad_limpia.lower() != 'nan':
                unidades.append(unidad_limpia)
            
            # Actualizar progreso cada 10 unidades
            if idx % 10 == 0 or idx == total_unidades:
                progress = 30 + int((idx / total_unidades) * 20)
                update_progress(progress, f"Procesando unidades... ({idx}/{total_unidades})")
        
        if not unidades:
            raise ValueError("No se encontraron unidades en el archivo")
        
        update_progress(50, f"Creando {len(unidades)} departamentos...")
        
        success_count = 0
        error_count = 0
        total_unidades = len(unidades)
        
        for idx, unidad in enumerate(unidades, 1):
            # Calcular progreso
            progress = 50 + int((idx / total_unidades) * 50)
            update_progress(progress, f"Creando departamentos... ({idx}/{total_unidades})", 
                        f"Procesando: {unidad[:30]}...")
            
            try:
                department = self.department_service.get_department_by_name(name=unidad)
                if not department:
                    department = self.department_service.create_department_f(name=unidad)
                    if department:
                        success_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                error_count += 1
        
        update_progress(100, "Finalizando...")
        
        return {
            'success': success_count,
            'errors': error_count,
            'total': len(unidades),
            'file': os.path.basename(file_path)
        }
    
    def _initialize_departments_from_file(self):
        """Inicializa departamentos desde archivo Excel"""
        from tkinter import messagebox
        
        try:
            result = self._run_with_progress(
                "Inicializando Departamentos",
                self._execute_departments_initialization
            )
            
            if result:
                if result['errors'] > 0:
                    messagebox.showinfo(
                        "✅ Inicialización parcial",
                        f"Inicialización completada:\n\n"
                        f"📄 Archivo: {result['file']}\n"
                        f"✅ Creados: {result['success']}\n"
                        f"❌ Errores: {result['errors']}\n"
                        f"📊 Total: {result['total']}"
                    )
                else:
                    messagebox.showinfo(
                        "✅ Inicialización exitosa",
                        f"Departamentos inicializados correctamente:\n\n"
                        f"📄 Archivo: {result['file']}\n"
                        f"📊 Total creados: {result['success']}"
                    )
        
        except Exception as e:
            if "Columnas faltantes" in str(e):
                messagebox.showerror(
                    "❌ Estructura incorrecta",
                    f"El archivo no tiene la estructura esperada.\n\n"
                    f"Columna requerida: 'Unidad'\n\n"
                    f"Por favor, use un archivo Excel con columna 'Unidad' "
                    f"que contenga los nombres de departamentos."
                )
            elif "No se encontraron unidades" in str(e):
                messagebox.showwarning(
                    "⚠️ Sin datos",
                    "No se encontraron unidades/departamentos en el archivo."
                )
            elif "archivo no existe" in str(e).lower():
                messagebox.showerror(
                    "❌ Archivo no encontrado",
                    "El archivo seleccionado no existe o no se puede acceder."
                )
            else:
                messagebox.showerror(
                    "❌ Error crítico",
                    f"Ocurrió un error inesperado:\n\n{str(e)}"
                )

    def _execute_request_users_initialization(self, update_progress):
        """Lógica interna para inicializar solicitantes con progreso"""
        from tkinter import filedialog
        import pandas as pd
        import os
        
        update_progress(0, "Verificando dependencias...")
        
        if not hasattr(self, 'department_service') or not self.department_service:
            raise ValueError("Servicio de departamentos no disponible")
        
        update_progress(5, "Seleccionando archivo...")
        
        file_path = filedialog.askopenfilename(
            title="📂 Seleccionar archivo Excel para solicitantes",
            initialdir=".",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not file_path:
            return None
        
        update_progress(10, "Verificando archivo...")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        update_progress(15, "Leyendo archivo Excel...")
        
        df = pd.read_excel(file_path, skiprows=3)
        
        required_columns = ['Nomre y apellidos', 'CI', 'Unidad']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Columnas faltantes: {', '.join(missing_columns)}")
        
        update_progress(20, "Procesando datos...")
        
        # CORRECCIÓN: Usar las columnas correctamente
        personas = []
        total_filas = len(df)
        
        for idx, row in df.iterrows():
            try:
                nombre = str(row['Nomre y apellidos']).strip()
                ci = str(row['CI']).strip()
                unidad = str(row['Unidad']).strip()
                
                if not nombre or nombre.lower() == 'nan' or nombre == 'None':
                    continue
                if not ci or ci.lower() == 'nan' or ci == 'None':
                    continue
                if len(ci) > 11:
                    continue
                
                personas.append({
                    'nombre': nombre,
                    'ci': ci,
                    'unidad': unidad
                })
            except Exception as e:
                continue
            
            # Actualizar progreso cada 50 filas
            if idx % 50 == 0 or idx == total_filas - 1:
                progress = 20 + int((idx / total_filas) * 30)
                update_progress(progress, f"Procesando datos... ({idx}/{total_filas})")
        
        if not personas:
            raise ValueError("No se encontraron personas con datos válidos en el archivo")
        
        update_progress(50, f"Creando {len(personas)} solicitantes...")
        
        success_count = 0
        error_count = 0
        dept_not_found = 0
        total_personas = len(personas)
        
        for idx, persona in enumerate(personas, 1):
            # Calcular progreso
            progress = 50 + int((idx / total_personas) * 50)
            update_progress(progress, f"Creando solicitantes... ({idx}/{total_personas})",
                        f"CI: {persona['ci']}")
            
            try:
                requ_user = self.request_user_service.get_user_by_ci(persona['ci'])
                if requ_user:
                    continue
                
                department = self.department_service.get_department_by_name(name=persona['unidad'])
                if not department:
                    dept_not_found += 1
                    continue
              
                
                user_data = RequestUserCreateDTO(
                    username=None,
                    fullname=persona['nombre'],
                    email=None,
                    ci=persona['ci'],
                    department_id=department.id
                )
                
                requ_user = self.request_user_service.create_user(user_data)
                
                if requ_user:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
        
        update_progress(100, "Finalizando...")
        
        return {
            'total': len(personas),
            'created': success_count,
            'dept_not_found': dept_not_found,
            'errors': error_count,
            'file': os.path.basename(file_path)
        } 
    
    def _initialize_request_users_from_file(self):
        """Inicializa solicitantes desde archivo Excel"""
        try:
            result = self._run_with_progress(
                "Inicializando Solicitantes",
                self._execute_request_users_initialization
            )
            
            if result:
                result_message = f"Inicialización completada:\n\n"
                result_message += f"📄 Archivo: {result['file']}\n"
                result_message += f"📊 Total procesados: {result['total']}\n"
                result_message += f"✅ Solicitantes creados: {result['created']}\n"
                result_message += f"❌ Errores: {result['errors']}\n"
                
                if result['dept_not_found'] > 0:
                    result_message += f"⚠️ Departamentos no encontrados: {result['dept_not_found']}\n"
                    result_message += "(Algunos solicitantes no pudieron ser creados por falta de departamento)"
                
                messagebox.showinfo("📊 Resultado", result_message)
        
        except Exception as e:
            if "Servicio de departamentos" in str(e):
                messagebox.showerror(
                    "❌ Servicio no disponible",
                    "Primero inicialice los departamentos."
                )
            elif "Columnas faltantes" in str(e):
                messagebox.showerror(
                    "❌ Estructura incorrecta",
                    f"El archivo debe contener las columnas:\n\n"
                    f"• 'Nomre y apellidos': Nombres completos\n"
                    f"• 'CI': Número de identificación\n"
                    f"• 'Unidad': Departamento asignado\n\n"
                    f"Verifique la estructura del archivo Excel."
                )
            elif "No se encontraron personas" in str(e):
                messagebox.showwarning(
                    "⚠️ Sin datos válidos",
                    "No se encontraron personas con datos válidos en el archivo."
                )
            else:
                messagebox.showerror("❌ Error", f"Error inesperado:\n\n{str(e)}")

    def _execute_cards_initialization(self, update_progress):
        """Lógica interna para inicializar tarjetas con progreso"""
        from tkinter import filedialog
        import pandas as pd
        import os
        
        update_progress(0, "Seleccionando archivo...")
        
        file_path = filedialog.askopenfilename(
            title="📂 Seleccionar archivo Excel para tarjetas",
            initialdir=".",
            filetypes=[
                ("Archivos Excel", "*.xls *.xlsx"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not file_path:
            return None
        
        update_progress(10, "Verificando archivo...")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        update_progress(20, "Leyendo archivo Excel...")
        
        df = pd.read_excel(file_path, skiprows=0)
        
        expected_column = 'Listado de tarjetas de Hospedaje '
        
        if expected_column not in df.columns:
            similar_columns = [col for col in df.columns if 'tarjeta' in str(col).lower() or 'hospedaje' in str(col).lower()]
            
            if similar_columns:
                raise ValueError(f"Columna esperada: '{expected_column}'\nColumnas similares: {', '.join(similar_columns)}")
            else:
                raise ValueError(f"Columna '{expected_column}' no encontrada")
        
        update_progress(30, "Procesando tarjetas...")
        
        dirty_data = df[expected_column]
        tarjetas_procesadas = 0
        tarjetas_creadas = 0
        tarjetas_existentes = 0
        errores = 0
        total_items = len(dirty_data)
        
        for idx, (index, number) in enumerate(dirty_data.items(), 1):
            try:
                number = str(number).strip()
                
                if not number or number.lower() in ['nan', 'none', 'null', '']:
                    continue
                
                tarjetas_procesadas += 1
                
                card = self.card_service.get_card_by_card_number(number)
                if not card:
                    card_number = number
                    card_pin = '0000'
                    amount = 0.00
                    
                    success = self.card_service.create_card(card_number, card_pin, amount)
                    if success:
                        tarjetas_creadas += 1
                    else:
                        errores += 1
                else:
                    tarjetas_existentes += 1
                    
            except Exception:
                errores += 1
            
            # Actualizar progreso cada 100 tarjetas
            if idx % 100 == 0 or idx == total_items:
                progress = 30 + int((idx / total_items) * 70)
                update_progress(progress, f"Procesando tarjetas... ({idx}/{total_items})")
        
        update_progress(100, "Finalizando...")
        
        return {
            'processed': tarjetas_procesadas,
            'created': tarjetas_creadas,
            'existing': tarjetas_existentes,
            'errors': errores,
            'file': os.path.basename(file_path)
        }
    
    def _initialize_cards_from_file(self):
        """Inicializa tarjetas desde archivo Excel"""
        try:
            result = self._run_with_progress(
                "Inicializando Tarjetas",
                self._execute_cards_initialization
            )
            
            if result:
                result_message = f"Inicialización completada:\n\n"
                result_message += f"📄 Archivo: {result['file']}\n"
                result_message += f"📊 Tarjetas procesadas: {result['processed']}\n"
                result_message += f"✅ Nuevas tarjetas: {result['created']}\n"
                result_message += f"ℹ️ Tarjetas existentes: {result['existing']}\n"
                
                if result['errors'] > 0:
                    result_message += f"❌ Errores: {result['errors']}\n\n"
                    result_message += "Algunas tarjetas no pudieron ser procesadas."
                
                messagebox.showinfo("💳 Resultado", result_message)
        
        except Exception as e:
            if "Columna esperada" in str(e):
                messagebox.showerror(
                    "❌ Estructura incorrecta",
                    f"El archivo debe contener la columna:\n\n"
                    f"'Listado de tarjetas de Hospedaje '\n\n"
                    f"Por favor, verifique el nombre de la columna."
                )
            elif "no encontrado" in str(e).lower():
                messagebox.showerror(
                    "❌ Archivo no encontrado",
                    "El archivo seleccionado no existe.\n\n"
                    "Por defecto se espera: 'Files/TARJETAS DE HOSPEDAJExlsx.xls'"
                )
            else:
                messagebox.showerror("❌ Error", f"Error inesperado:\n\n{str(e)}")

    def _initialize_diet_services(self):
        """Inicializa los servicios de dieta por defecto"""
        try:
            result = self._run_with_progress(
                "Inicializando Servicios de Dieta",
                self._execute_diet_services_initialization
            )
            
            if result:
                if result['local'] and result['foreign']:
                    messagebox.showinfo(
                        "✅ Servicios creados",
                        "Servicios de dieta inicializados correctamente."
                    )
                elif result['local'] or result['foreign']:
                    messagebox.showwarning(
                        "⚠️ Inicialización parcial",
                        f"Servicio local: {'✅' if result['local'] else '❌'}\n"
                        f"Servicio foráneo: {'✅' if result['foreign'] else '❌'}"
                    )
                else:
                    messagebox.showerror("❌ Error", "No se pudieron crear los servicios.")
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error inesperado:\n\n{str(e)}")

    def _execute_diet_services_initialization(self, update_progress):
        """Lógica interna para inicializar servicios de dieta con progreso"""
        update_progress(0, "Verificando servicios existentes...")
        
        service_local = self.diet_service.get_diet_service_by_local(True)
        service_foreign = self.diet_service.get_diet_service_by_local(False)
        
        update_progress(30, "Creando servicios...")
        
        try:
            diet_service_local = DietServiceCreateDTO(
                is_local=True,
                breakfast_price=200,
                lunch_price=200,
                dinner_price=200,
                accommodation_cash_price=200,
                accommodation_card_price=200
            )
            success_local = self.diet_service.create_diet_service(diet_service_local)
        except Exception:
            success_local = False
        
        update_progress(60, "Creando servicio foráneo...")
        
        try:
            diet_service_foreign = DietServiceCreateDTO(
                is_local=False,
                breakfast_price=300,
                lunch_price=300,
                dinner_price=300,
                accommodation_cash_price=300,
                accommodation_card_price=300
            )
            success_foreign = self.diet_service.create_diet_service(diet_service_foreign)
        except Exception:
            success_foreign = False
        
        update_progress(100, "Finalizando...")
        
        return {
            'local': success_local,
            'foreign': success_foreign
        }

    def _initialize_admin_user(self):
        """Inicializa el usuario administrador por defecto"""
        admin_user = self.user_service.get_user_by_username("admin")
        
        if admin_user:
            messagebox.showinfo(
                "✅ Usuario existente",
                "El usuario administrador ya existe.\n\n"
                "Usuario: admin\n\n"
                "Use la opción de gestión de usuarios para cambiar la contraseña."
            )
            return
        
        try:
            admin_user = self.user_service.create_user(
                username="admin",
                email="admin@dietasapp.com",
                password="admin01*",
                role=UserRole.ADMIN
            )
            
            if admin_user:
                messagebox.showinfo(
                    "✅ Usuario creado",
                    "Usuario administrador creado exitosamente.\n\n"
                    "Usuario: admin\nContraseña: admin01*\n\n"
                    "Cambie la contraseña después del primer inicio."
                )
            else:
                messagebox.showerror("❌ Error", "No se pudo crear el usuario.")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error creando usuario:\n\n{str(e)}")

    def _initialize_all_from_files(self):
        """Ejecuta todas las inicializaciones en orden"""
        
        def execute_complete_initialization(update_progress):
            resultados = {}
            
            update_progress(0, "Iniciando inicialización completa...")
            
            # 1. Departamentos
            update_progress(10, "Paso 1/5: Inicializando departamentos...")
            resultados['departamentos'] = self._execute_departments_initialization(update_progress)
            
            # 2. Solicitantes
            update_progress(40, "Paso 2/5: Inicializando solicitantes...")
            if resultados['departamentos'] and resultados['departamentos'].get('success', 0) > 0:
                resultados['solicitantes'] = self._execute_request_users_initialization(update_progress)
            else:
                resultados['solicitantes'] = {'error': 'Sin departamentos creados'}
            
            # 3. Tarjetas
            update_progress(60, "Paso 3/5: Inicializando tarjetas...")
            resultados['tarjetas'] = self._execute_cards_initialization(update_progress)
            
            # 4. Servicios de dieta
            update_progress(80, "Paso 4/5: Inicializando servicios de dieta...")
            resultados['servicios'] = self._execute_diet_services_initialization(update_progress)
            
            # 5. Usuario admin
            update_progress(90, "Paso 5/5: Inicializando usuario administrador...")
            resultados['admin'] = self._initialize_admin_user()
            
            update_progress(100, "Inicialización completa finalizada")
            return resultados
        
        try:
            result = self._run_with_progress(
                "Inicialización Completa",
                execute_complete_initialization
            )
            
            if result:
                self._show_initialization_summary(result)
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error en inicialización:\n\n{str(e)}")

    def _initialize_diet_services_internal(self):
        """Versión interna para inicialización completa"""
        try:
            diet_service_local = DietServiceCreateDTO(
                is_local=True,
                breakfast_price=200,
                lunch_price=200,
                dinner_price=200,
                accommodation_cash_price=200,
                accommodation_card_price=200
            )
            success_local = self.diet_service.create_diet_service(diet_service_local)
        except Exception:
            success_local = False
        
        try:
            diet_service_foreign = DietServiceCreateDTO(
                is_local=False,
                breakfast_price=300,
                lunch_price=300,
                dinner_price=300,
                accommodation_cash_price=300,
                accommodation_card_price=300
            )
            success_foreign = self.diet_service.create_diet_service(diet_service_foreign)
        except Exception:
            success_foreign = False
        
        return {
            'local': success_local,
            'foreign': success_foreign
        }

    def _initialize_admin_user_internal(self):
        """Versión interna para inicialización completa"""
        admin_user = self.user_service.get_user_by_username("admin")
        
        if not admin_user:
            try:
                admin_user = self.user_service.create_user(
                    username="admin",
                    email="admin@dietasapp.com",
                    password="admin01*",
                    role=UserRole.ADMIN
                )
                return {'created': True, 'user': 'admin'}
            except Exception:
                return {'created': False, 'error': 'Error creando usuario'}
        
        return {'created': False, 'message': 'Ya existe'}

    def _show_initialization_summary(self, result):
        """Muestra resumen de inicialización completa"""
        resumen = "📊 RESUMEN DE INICIALIZACIÓN\n\n"
        
        if 'departamentos' in result and result['departamentos']:
            dept = result['departamentos']
            resumen += f"📂 Departamentos: ✅ {dept.get('success', 0)}/{dept.get('total', 0)}\n"
        else:
            resumen += "📂 Departamentos: ❌\n"
        
        if 'solicitantes' in result and result['solicitantes']:
            sol = result['solicitantes']
            if 'error' in sol:
                resumen += f"👥 Solicitantes: ❌ {sol['error']}\n"
            else:
                resumen += f"👥 Solicitantes: ✅ {sol.get('created', 0)}/{sol.get('total', 0)}\n"
        else:
            resumen += "👥 Solicitantes: ❌\n"
        
        if 'tarjetas' in result and result['tarjetas']:
            cards = result['tarjetas']
            resumen += f"💳 Tarjetas: ✅ {cards.get('created', 0)}/{cards.get('processed', 0)}\n"
        else:
            resumen += "💳 Tarjetas: ❌\n"
        
        if 'servicios' in result and result['servicios']:
            serv = result['servicios']
            local = '✅' if serv.get('local') else '❌'
            foreign = '✅' if serv.get('foreign') else '❌'
            resumen += f"🍽️ Servicios: {local} local, {foreign} foráneo\n"
        else:
            resumen += "🍽️ Servicios: ❌\n"
        
        if 'admin' in result and result['admin']:
            admin = result['admin']
            if admin.get('created'):
                resumen += "👨‍💼 Admin: ✅ Creado\n"
            else:
                resumen += f"👨‍💼 Admin: ℹ️ {admin.get('message', '')}\n"
        else:
            resumen += "👨‍💼 Admin: ❌\n"
        
        messagebox.showinfo("📋 Resultado Final", resumen)
    
    def _show_user_manual(self):
        """Muestra el manual de usuario"""
        manual_text = """📖 MANUAL DE USUARIO - Sistema de Gestión de Dietas

    1. 📋 CONCEPTOS BÁSICOS:
    • Dieta: Anticipo económico para gastos de alimentación/alojamiento
    • Liquidación: Rendición de cuentas de una dieta utilizada
    • Solicitante: Persona que solicita una dieta
    • Tarjeta: Medio de pago para alojamiento

    2. 🏢 MÓDULOS PRINCIPALES:

    a) GESTIÓN DE SOLICITANTES:
        • Registrar nuevos solicitantes
        • Asignar departamento
        • Ver historial de dietas

    b) GESTIÓN DE DIETAS:
        • Crear nuevo anticipo
        • Especificar tipo (local/foráneo)
        • Calcular montos automáticamente
        • Generar solicitud

    c) LIQUIDACIONES:
        • Registrar gastos realizados
        • Adjuntar solicitud
        • Calcular saldos
        • Generar reporte final

    d) TARJETAS DE HOSPEDAJE:
        • Asignar tarjetas a solicitudes
        • Control de saldos
        • Historial de uso

    3. ⚙️ CONFIGURACIÓN INICIAL:

    PASO 1: Inicializar Departamentos
        • Ir a: Configuración → Inicialización → Departamentos desde Excel
        • Requiere archivo Excel con columna 'Unidad' donde se mencionen los departamentos

    PASO 2: Inicializar Solicitantes  
        • Ir a: Configuración → Inicialización → Solicitantes desde Excel
        • Requiere archivo con columnas: 'Nomre y apellidos', 'CI', 'Unidad'
        • Requiere la carga previa de los departamentos

    PASO 3: Inicializar Tarjetas
        • Ir a: Configuración → Inicialización → Tarjetas desde Excel
        • Requiere archivo con columna: 'Listado de tarjetas de Hospedaje '

    PASO 4: Configurar Precios
        • Ir a: Configuración → Inicialización → Servicios de Dieta
        • Establecer precios para servicios locales y foráneos
        • Luego de creados los precios por defecto pueden ser modificados libremente en el módulo de Dietas, seccion de Gestión de Servicios

    4. 🔄 FLUJO DE TRABAJO TÍPICO:

    a) NUEVA DIETA:
        1. Seleccionar solicitante(s)
        2. Especificar tipo de dieta (local/foráneo)
        3. Ingresar descripción, fechas y servicios requeridos
        4. Sistema calcula montos automáticamente
        5. Generar solicitud de anticipo

    b) LIQUIDAR DIETA:
        1. Seleccionar dieta a liquidar
        2. Registrar servicios reales realizados
        3. Sistema adjuntar solicitudes escaneadas
        4. Calcular diferencia (favor/contra)
        5. Generar reporte de liquidación

    5. 💾 ADMINISTRACIÓN:

    a) BACKUP:
        • Configuración → Backup Base de Datos
        • Se recomienda realizar al menos una vez al mes

    b) NUEVO CICLO:
        • Configuración → Iniciar Nuevo Ciclo
        • Mantiene datos maestros, elimina dietas antiguas
        • Ideal al comenzar nuevo período contable (Año)

    6. 🚨 SOLUCIÓN DE PROBLEMAS:

    • Error al leer Excel: Verificar formato y nombres de columnas (Deben tener nombres exactos a como aparecen en la ayuda )
    • Datos incorrectos: Verificar archivos fuente
    • Pérdida de datos: Restaurar desde backup
    • Bloqueos: Cerrar la aplicación y volver a abrir
    • Otros: Contactar soporte

    7. 📞 SOPORTE:
    • Contacto: jayler@cimex.com.cu
    • Teléfono: 41 360204 - IP: 1204
    • Horario: L-V 8:00 AM - 5:30 PM

    Versión del Manual: 1.0 - Enero 2024"""
        
        self._show_help_window("Manual de Usuario", manual_text, width=800, height=600)

    def _show_documentation(self):
        """Muestra documentación técnica"""
        docs_text = """📚 DOCUMENTACIÓN TÉCNICA

    ESTRUCTURA DEL SISTEMA:

    1. 🗄️ ARQUITECTURA:
    • Base de datos: SQLite (dietas_app.db)
    • Backups: Carpeta 'SalvasDietas'
    • Ciclos: Carpeta 'Ciclos'
    

    2. 📁 ESTRUCTURA DE ARCHIVOS:
    dietas_app/
    ├── dietas_app.db              # Base de datos principal
    ├── SalvasDietas/              # Backups automáticos
    │   ├── backup_descripcion_YYYYMMDD_HHMMSS.db
    │   └── ciclo_nombre_YYYYMMDD_HHMMSS.db
    ├── Ciclos/                    # Reportes de nuevos ciclos
    │   └── reporte_ciclo_YYYYMMDD_HHMMSS.txt
    ├── Files/                     # Archivos de inicialización
        ├── Maestro de trabajadores cierre septiembre.xlsx
        └── TARJETAS DE HOSPEDAJExlsx.xls


    3. 🗃️ ESTRUCTURA DE LA BASE DE DATOS:

    # Reservada

    4. 🔐 SEGURIDAD:
    • Autenticación por usuario/contraseña
    • Roles: ADMIN, MANAGER, USER
    • Contraseñas encriptadas

    5. 📊 FORMATOS DE ARCHIVOS SOPORTADOS:

    INICIALIZACIÓN:
    • Excel (.xlsx, .xls)
    • Columnas específicas requeridas

    EXPORTACIÓN:
    • Excel (.xlsx)
    • PDF (reportes)

    6. ⚙️ CONFIGURACIÓN:

    ARCHIVOS DE CONFIGURACIÓN:
    • settings.json: Preferencias de usuario
    • REINICIAR_APP.txt: Indicador de restauración
    • APP_BLOQUEADA.lock: Bloqueo post-operación

    7. 🐛 DIAGNÓSTICO:

    8. 🔄 MIGRACIONES:

    PROCEDIMIENTO PARA ACTUALIZAR:
    1. Realizar backup completo
    2. Detener aplicación
    3. Iniciar aplicación
    4. Verificar integridad

    VERSIÓN: 1.0.0 - Sistema de Gestión de Dietas"""
        
        self._show_help_window("Documentación Técnica", docs_text, width=850, height=650)

    def _show_support_info(self):
        """Muestra información de soporte técnico"""
        support_text = """🛠️ SOPORTE TÉCNICO

    INFORMACIÓN DE CONTACTO:

    📧 CORREO ELECTRÓNICO:
    • Soporte General: jayler@cimex.com.cu
    • Desarrollo: jayler@cimex.com.cu
    • Administración: jayler@cimex.com.cu

    📞 TELÉFONOS:
    • Soporte Técnico: 41 360204 - IP: 1204
    • Emergencias: 41 360207 - IP: 1207

    🕐 HORARIOS DE ATENCIÓN:
    • Lunes a Viernes: 8:00 AM - 5:30 PM

    📍 OFICINAS:
    • Oficina Informática: Sucursal Sancti Spíritus

    PROCEDIMIENTOS DE SOPORTE:

    📝 AL REPORTAR UN PROBLEMA:

    INFORMACIÓN REQUERIDA:
    1. Descripción detallada del problema
    2. Pasos para reproducirlo
    3. Capturas de pantalla (si es posible)
    4. Archivos involucrados

    EJEMPLO:
    "Al intentar crear una dieta para el solicitante Juan Pérez, 
    el sistema muestra error 'Clave foránea no encontrada'. 
    Ocurrió hoy 15/01/2024 a las 10:30 AM."

    🔧 AUTOAYUDA:

    PROBLEMAS COMUNES Y SOLUCIONES:

    a) ERROR AL LEER ARCHIVO EXCEL:
        • Verifique que el archivo no esté abierto en otro programa
        • Confirme nombres de columnas requeridas
        • Valide formato de archivo (.xlsx, .xls)

    b) LENTITUD DEL SISTEMA:
        • Elimine backups antiguos innecesarios
        • Reinicie la aplicación

    c) ERROR 'FOREIGN KEY CONSTRAINT FAILED':
        • Asegúrese de inicializar departamentos primero
        • Verifique integridad de datos en Excel
        • Contacte soporte si persiste

    d) NO SE PUEDE CREAR NUEVO CICLO:
        • Verifique permisos de escritura en carpeta
        • Asegúrese de tener espacio en disco
        • Realice backup manual antes de intentar


    📚 RECURSOS ADICIONALES:
    • Manual de Usuario: Ayuda → Manual de Usuario"""
        
        self._show_help_window("Soporte Técnico", support_text, width=900, height=700)

    def _show_about(self):
            """Muestra información acerca de la aplicación"""
            from datetime import datetime
            
            about_text = f"""ℹ️ ACERCA DE DIETAS APP

        📊 SISTEMA DE GESTIÓN DE DIETAS
        Versión: 1.0.0
        Fecha de compilación: {datetime.now().strftime('%d/%m/%Y')}

        DESARROLLADO POR:
        • Equipo de Desarrollo Cimex Sucursal Sancti'Spíritus
        • Contactos: 
                    jayler@cimex.com.cu
                    jailerpc@cimex.com.cu
                    dlamargo@cimex.com.cu

        © {datetime.now().year} - Todos los derechos reservados.

        📋 LICENCIA:
        Este software es propiedad de Cimex Sucursal Sancti'Spíritus.
        Uso autorizado únicamente para sus clientes registrados.

        ⚙️ TECNOLOGÍAS UTILIZADAS:
        • Python 3.12+
        • SQLite 3
        • Tkinter para interfaz gráfica
        • Pandas para procesamiento de datos

        🌐 IDIOMAS SOPORTADOS:
        • Español (predeterminado)

        📞 SOPORTE:
        • Email: jayler@cimex.com.cu
        • Teléfono: 47 360204 - IP: 1204
        • Horario: L-V 8:00 AM - 5:30 PM

        🔒 SEGURIDAD:
        • Encriptación de contraseñas
        • Backups semi-automáticos
        • Control de acceso por roles
        • Registro de actividades

        📈 ESTADÍSTICAS DEL SISTEMA:
        • Base de datos: SQLite
        • Backups: Carpeta 'SalvasDietas'
        • Ciclos: Carpeta 'ciclos'
        • Usuarios soportados: Ilimitados
        • Dietas por ciclo: Ilimitadas

        🙏 AGRADECIMIENTOS ESPECIALES:
        A todos nuestros usuarios por sus valiosos comentarios
        y sugerencias que han ayudado a mejorar este sistema.

        ⚠️ ADVERTENCIA:
        Este software es para uso interno de la organización.
        No comparta credenciales de acceso con personas no autorizadas.

        ¡GRACIAS POR UTILIZAR DIETAS APP!"""
            
            self._show_help_window("Acerca de", about_text, width=700, height=500)

    def _show_help_window(self, title: str, content: str, width: int = 750, height: int = 550):
        """Ventana genérica para mostrar contenido de ayuda"""
        help_window = tk.Toplevel(self.root)
        help_window.title(title)
        help_window.geometry(f"{width}x{height}")
        help_window.resizable(True, True)
        help_window.transient(self.root)
        
        # Frame principal
        main_frame = ttk.Frame(help_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Texto con scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled', bg='#f5f5f5')
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botón para copiar contenido
        ttk.Button(button_frame, text="📋 Copiar al portapapeles", 
                command=lambda: self._copy_to_clipboard(content)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para imprimir
        ttk.Button(button_frame, text="🖨️ Imprimir", 
                command=lambda: self._print_content(title, content)).pack(side=tk.LEFT, padx=10)
        
        # Botón para cerrar
        ttk.Button(button_frame, text="Cerrar", 
                command=help_window.destroy).pack(side=tk.RIGHT)
        
        # Centrar ventana
        self._center_window(help_window)

    def _copy_to_clipboard(self, text: str):
        """Copia texto al portapapeles"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copiado", "Texto copiado al portapapeles.")

    def _print_content(self, title: str, content: str):
        """Imprime contenido """
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=f"{title.replace(' ', '_')}.txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Guardado", f"Contenido guardado en:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def _center_window(self, window):
        """Centra una ventana en la pantalla"""
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width // 2) - (window.winfo_width() // 2)
        y = (screen_height // 2) - (window.winfo_height() // 2)
        
        window.geometry(f"+{x}+{y}")

    def _manage_accounts(self):
        """Abrir diálogo de gestión de cuentas"""
        if not hasattr(self, 'account_service') or self.account_service is None:
            messagebox.showerror("Error", "Servicio de cuentas no disponible")
            return
        
        try:
            from presentation.gui.account_presentation.dialogs.account_management_dialog import AccountManagementDialog
            
            dialog = AccountManagementDialog(self.root, self.account_service)
            dialog.wait_window()  # Diálogo modal
        except ImportError as e:
            messagebox.showerror("Error", f"Módulo no disponible: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir gestión de cuentas: {str(e)}")