# presentation/gui/config_presentation/settings_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AppSettings:
    """Configuración de la aplicación"""
    theme: str = "blue"
    language: str = "es"
    auto_save: bool = True
    auto_save_interval: int = 5 
    notifications_enabled: bool = True
    default_currency: str = "USD"
    date_format: str = "%d/%m/%Y"

class SettingsWindow(tk.Toplevel):
    """Ventana de configuración del sistema"""
    
    def __init__(self, parent, settings_service=None, database_service=None ):
        super().__init__(parent)
        self.settings_service = settings_service
        self.database_service = database_service
        self.settings = AppSettings()
        
        self.title("Configuración del Sistema")
        self.geometry("700x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._load_settings()
        self._create_widgets()
        self._center_on_parent()
        
    def _center_on_parent(self):
        """Centra la ventana sobre su padre"""
        self.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width // 2) - (self.winfo_width() // 2)
        y = parent_y + (parent_height // 2) - (self.winfo_height() // 2)
        
        self.geometry(f"+{x}+{y}")
    
    def _load_settings(self):
        """Carga la configuración desde el servicio"""
        if self.settings_service:
            try:
                self.settings = self.settings_service.get_settings()
            except:
                pass  # Usa valores por defecto
    
    def _create_widgets(self):
        """Crea los widgets de configuración"""
        # Notebook para pestañas
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña General
        general_frame = ttk.Frame(notebook)
        self._create_general_tab(general_frame)
        notebook.add(general_frame, text="General")
        
        # Pestaña Apariencia
        appearance_frame = ttk.Frame(notebook)
        self._create_appearance_tab(appearance_frame)
        notebook.add(appearance_frame, text="Apariencia")
        
        # Pestaña Base de Datos
        db_frame = ttk.Frame(notebook)
        self._create_database_tab(db_frame)
        notebook.add(db_frame, text="Base de Datos")
        
        # Botones de acción
        self._create_action_buttons()
    
    def _create_general_tab(self, parent):
        """Crea la pestaña de configuración general"""
        frame = ttk.LabelFrame(parent, text="Configuración General", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Idioma
        ttk.Label(frame, text="Idioma:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value=self.settings.language)
        language_combo = ttk.Combobox(frame, textvariable=self.language_var, 
                                    values=["es", "en", "fr", "de"], width=15)
        language_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Moneda por defecto
        ttk.Label(frame, text="Moneda:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.currency_var = tk.StringVar(value=self.settings.default_currency)
        currency_combo = ttk.Combobox(frame, textvariable=self.currency_var,
                                     values=["USD", "EUR", "COP", "MXN"], width=15)
        currency_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Formato de fecha
        ttk.Label(frame, text="Formato de fecha:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.date_format_var = tk.StringVar(value=self.settings.date_format)
        date_formats = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"]
        date_combo = ttk.Combobox(frame, textvariable=self.date_format_var,
                                 values=date_formats, width=15)
        date_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
    
    def _create_appearance_tab(self, parent):
        """Crea la pestaña de apariencia"""
        frame = ttk.LabelFrame(parent, text="Apariencia", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tema
        ttk.Label(frame, text="Tema:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar(value=self.settings.theme)
        themes = ["light", "dark", "blue", "green", "purple"]
        theme_combo = ttk.Combobox(frame, textvariable=self.theme_var,
                                  values=themes, width=15)
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Tamaño de fuente
        ttk.Label(frame, text="Tamaño de fuente:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.IntVar(value=10)
        font_scale = ttk.Scale(frame, from_=8, to=16, variable=self.font_size_var,
                              orient=tk.HORIZONTAL, length=150)
        font_scale.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Checkboxes
        self.compact_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Modo compacto", 
                       variable=self.compact_mode_var).grid(row=2, column=0, 
                                                          columnspan=2, 
                                                          sticky=tk.W, pady=5)
        
        self.show_icons_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Mostrar iconos", 
                       variable=self.show_icons_var).grid(row=3, column=0,
                                                        columnspan=2,
                                                        sticky=tk.W, pady=5)
    
    def _create_database_tab(self, parent):
        """Crea la pestaña de base de datos - VERSIÓN MEJORADA"""
        frame = ttk.LabelFrame(parent, text="Base de Datos", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Información de la base de datos
        info_frame = ttk.Frame(frame)
        info_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, 15))
        
        ttk.Label(info_frame, text="Información de la base de datos:", 
                font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.db_info_text = tk.StringVar(value="Cargando información...")
        ttk.Label(info_frame, textvariable=self.db_info_text, 
                wraplength=400).pack(anchor=tk.W, pady=(5, 0))
        
        # Botones de acción DB
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=tk.W)
        
        ttk.Button(btn_frame, text="🔄 Actualizar Info", 
                command=self._refresh_db_info).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="💾 Crear Backup", 
                command=self._perform_backup).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="⚙️ Optimizar BD", 
                command=self._optimize_database).pack(side=tk.LEFT)
        
        # Lista de backups
        backup_frame = ttk.LabelFrame(frame, text="Backups Disponibles", padding=10)
        backup_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S, pady=(15, 0))
        
        # Crear Treeview para backups
        columns = ("Fecha", "Nombre", "Tamaño", "Acciones")
        self.backup_tree = ttk.Treeview(backup_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=100)
        
        self.backup_tree.column("Fecha", width=150)
        self.backup_tree.column("Nombre", width=200)
        self.backup_tree.column("Tamaño", width=100)
        self.backup_tree.column("Acciones", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(backup_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backup_tree.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        # Frame para botones de backup
        backup_btn_frame = ttk.Frame(backup_frame)
        backup_btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
        
        ttk.Button(backup_btn_frame, text="↻ Actualizar Lista", 
                command=self._refresh_backup_list).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(backup_btn_frame, text="📥 Restaurar Seleccionado", 
                command=self._restore_selected_backup, 
                style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(backup_btn_frame, text="🗑️ Eliminar Seleccionado", 
                command=self._delete_selected_backup).pack(side=tk.LEFT)
        
        # Configurar expansión
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        backup_frame.columnconfigure(0, weight=1)
        backup_frame.rowconfigure(0, weight=1)
        
        # Cargar información inicial
        self._refresh_db_info()
        self._refresh_backup_list()
    
    def _create_action_buttons(self):
        """Crea los botones de acción"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Guardar", 
                  command=self._save_settings, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Aplicar", 
                  command=self._apply_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Restaurar Valores por Defecto", 
                  command=self._restore_defaults).pack(side=tk.LEFT)
     
    def _apply_settings(self):
        """Aplica la configuración sin cerrar"""
        self._save_to_settings_object()
        messagebox.showinfo("Configuración", "Configuración aplicada correctamente")
    
    def _save_settings(self):
        """Guarda la configuración y cierra"""
        self._save_to_settings_object()
        if self.settings_service:
            self.settings_service.save_settings(self.settings)
        messagebox.showinfo("Configuración", "Configuración guardada correctamente")
        self.destroy()
    
    def _save_to_settings_object(self):
        """Actualiza el objeto settings con los valores de la UI"""
        self.settings.language = self.language_var.get()
        self.settings.default_currency = self.currency_var.get()
        self.settings.date_format = self.date_format_var.get()
        self.settings.theme = self.theme_var.get()

    def _refresh_db_info(self):
        """Actualiza la información de la base de datos"""
        if self.database_service:
            try:
                info = self.database_service.get_database_info()
                
                if info['exists']:
                    text = (f"Ubicación: {info['path']}\n"
                        f"Tamaño: {info.get('size_mb', 0):.2f} MB\n"
                        f"Última modificación: {info.get('modified', 'N/A')}\n"
                        f"Backups disponibles: {info['backup_count']}")
                else:
                    text = f"Base de datos no encontrada en: {info['path']}"
                    
                self.db_info_text.set(text)
            except Exception as e:
                self.db_info_text.set(f"Error cargando información: {str(e)}")

    def _refresh_backup_list(self):
        """Actualiza la lista de backups"""
        if not self.database_service:
            return
        
        # Limpiar lista actual
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        try:
            backups = self.database_service.get_backup_list()
            
            for backup_path, backup_date, size_bytes in backups:
                # Formatear tamaño
                if size_bytes > 1024 * 1024:  # MB
                    size_str = f"{size_bytes/(1024*1024):.2f} MB"
                elif size_bytes > 1024:  # KB
                    size_str = f"{size_bytes/1024:.1f} KB"
                else:
                    size_str = f"{size_bytes} bytes"
                
                # Insertar en treeview
                self.backup_tree.insert("", tk.END, values=(
                    backup_date.strftime("%Y-%m-%d %H:%M:%S"),
                    backup_path.name,
                    size_str,
                    "📥 Restaurar | 🗑️ Eliminar"
                ), tags=(str(backup_path),))
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los backups: {str(e)}")

    def _perform_backup(self):
        """Realiza backup de la base de datos"""
        if not self.database_service:
            messagebox.showerror("Error", "Servicio de base de datos no disponible 3")
            return
        
        # Pedir descripción opcional
        description = simpledialog.askstring(
            "Descripción del Backup",
            "Ingrese una descripción opcional para el backup (presione Cancelar para omitir):",
            parent=self
        )
        
        try:
            backup_path = self.database_service.create_backup(description)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Backup Exitoso",
                f"Backup creado exitosamente en:\n"
                f"{backup_path}\n\n"
                f"Total de backups: {len(list(Path('SalvasDietas').glob('*.db')))}"
            )
            
            # Actualizar listas
            self._refresh_db_info()
            self._refresh_backup_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el backup: {str(e)}")

    def _restore_selected_backup(self):
        """Restaura el backup seleccionado"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor, seleccione un backup de la lista")
            return
        
        item = selection[0]
        backup_path = Path(self.backup_tree.item(item, "tags")[0])
        
        # Confirmar restauración
        if not messagebox.askyesno(
            "Confirmar Restauración",
            f"¿Está seguro de restaurar el backup?\n\n"
            f"Archivo: {backup_path.name}\n\n"
            f"⚠️ ADVERTENCIA: Esto sobrescribirá la base de datos actual.\n"
            f"Se creará un backup de la BD actual antes de restaurar."
        ):
            return
        
        try:
            if self.database_service.restore_backup(backup_path):
                messagebox.showinfo(
                    "Restauración Exitosa",
                    f"Backup restaurado exitosamente.\n\n"
                    f"La aplicación debe reiniciarse para aplicar los cambios.\n"
                    f"¿Desea reiniciar ahora?"
                )
                # Aquí podrías agregar lógica para reiniciar la app
                self._refresh_db_info()
                self._refresh_backup_list()
            else:
                messagebox.showerror("Error", "No se pudo restaurar el backup")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error restaurando backup: {str(e)}")

    def _delete_selected_backup(self):
        """Elimina el backup seleccionado"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor, seleccione un backup de la lista")
            return
        
        item = selection[0]
        backup_path = Path(self.backup_tree.item(item, "tags")[0])
        
        if not messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el backup?\n\n"
            f"Archivo: {backup_path.name}\n\n"
            f"Esta acción no se puede deshacer."
        ):
            return
        
        try:
            if self.database_service.delete_backup(backup_path):
                messagebox.showinfo("Éxito", "Backup eliminado correctamente")
                self._refresh_db_info()
                self._refresh_backup_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el backup")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error eliminando backup: {str(e)}")

    def _optimize_database(self):
        """Optimiza la base de datos"""
        if not self.database_service:
            return
        
        if not messagebox.askyesno(
            "Optimizar Base de Datos",
            "¿Desea optimizar la base de datos?\n\n"
            "Esto puede tomar algunos segundos y mejorará el rendimiento."
        ):
            return
        
        try:
            if self.database_service.optimize_database():
                messagebox.showinfo("Éxito", "Base de datos optimizada correctamente")
                self._refresh_db_info()
            else:
                messagebox.showerror("Error", "No se pudo optimizar la base de datos")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error optimizando base de datos: {str(e)}")