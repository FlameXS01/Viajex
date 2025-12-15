# presentation/gui/config_presentation/settings_window.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

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
    current_database: str = "dietas_app.db"

class SettingsWindow(tk.Toplevel):
    """Ventana de configuración del sistema optimizada"""
    
    def __init__(self, parent, settings_service=None, database_service=None):
        super().__init__(parent)
        self.settings_service = settings_service
        self.database_service = database_service
        self.settings = AppSettings()
        self.selected_backup_path = None
        
        self._setup_window()
        self._load_settings()
        self._create_widgets()
        self._center_on_parent()
        self._bind_events()
    
    def _setup_window(self):
        """Configura la ventana principal"""
        self.title("Configuración del Sistema")
        self.geometry("750x550")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        
        # Configurar estilos
        self.style = ttk.Style()
        self.style.configure('Accent.TButton', foreground='blue', font=('Arial', 10, 'bold'))
    
    def _center_on_parent(self):
        """Centra la ventana sobre su padre"""
        self.update_idletasks()
        parent = self.master
        
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        
        self.geometry(f"+{x}+{y}")
    
    def _load_settings(self):
        """Carga la configuración desde el servicio"""
        if self.settings_service:
            try:
                loaded = self.settings_service.get_settings()
                if loaded:
                    self.settings = loaded
            except Exception as e:
                logger.error(f"Error cargando configuración: {e}")
    
    def _create_widgets(self):
        """Crea todos los widgets"""
        # Notebook para pestañas
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self._create_general_tab(notebook)
        self._create_appearance_tab(notebook)
        self._create_database_tab(notebook)
        
        # Botones de acción
        self._create_action_buttons()
    
    def _create_general_tab(self, notebook):
        """Crea la pestaña de configuración general"""
        frame = ttk.Frame(notebook)
        
        content = ttk.LabelFrame(frame, text="Configuración General", padding=15)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Idioma
        ttk.Label(content, text="Idioma:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value=self.settings.language)
        ttk.Combobox(content, textvariable=self.language_var, 
                    values=["es", "en", "fr", "de"], 
                    width=15, state="readonly").grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Moneda
        ttk.Label(content, text="Moneda:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.currency_var = tk.StringVar(value=self.settings.default_currency)
        ttk.Combobox(content, textvariable=self.currency_var,
                    values=["USD", "EUR", "COP", "MXN"], 
                    width=15, state="readonly").grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Formato de fecha
        ttk.Label(content, text="Formato de fecha:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.date_format_var = tk.StringVar(value=self.settings.date_format)
        ttk.Combobox(content, textvariable=self.date_format_var,
                    values=["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"], 
                    width=15, state="readonly").grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Auto-guardado
        self.auto_save_var = tk.BooleanVar(value=self.settings.auto_save)
        ttk.Checkbutton(content, text="Auto-guardado", 
                       variable=self.auto_save_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        notebook.add(frame, text="General")
    
    def _create_appearance_tab(self, notebook):
        """Crea la pestaña de apariencia"""
        frame = ttk.Frame(notebook)
        
        content = ttk.LabelFrame(frame, text="Apariencia", padding=15)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tema
        ttk.Label(content, text="Tema:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar(value=self.settings.theme)
        ttk.Combobox(content, textvariable=self.theme_var,
                    values=["light", "dark", "blue", "green", "purple"], 
                    width=15, state="readonly").grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        notebook.add(frame, text="Apariencia")
    
    def _create_database_tab(self, notebook):
        """Crea la pestaña de base de datos mejorada"""
        frame = ttk.Frame(notebook)
        
        # Panel de información
        info_frame = ttk.LabelFrame(frame, text="Información de Base de Datos", padding=15)
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.info_text = tk.Text(info_frame, height=6, width=70, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        
        # Botones de acción
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="🔄 Actualizar", 
                  command=self._refresh_db_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="💾 Crear Backup", 
                  command=self._perform_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⚙️ Optimizar", 
                  command=self._optimize_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🆕 Nuevo Ciclo", 
                  command=self._start_new_cycle, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Lista de backups
        list_frame = ttk.LabelFrame(frame, text="Backups Disponibles", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Treeview para backups
        columns = ("Fecha", "Nombre", "Tamaño", "Tipo")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configurar columnas
        col_widths = {"Fecha": 150, "Nombre": 250, "Tamaño": 100, "Tipo": 100}
        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=col_widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backup_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # Botones de backup
        backup_btn_frame = ttk.Frame(list_frame)
        backup_btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
        
        ttk.Button(backup_btn_frame, text="↻ Actualizar", 
                  command=self._refresh_backup_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(backup_btn_frame, text="📥 Restaurar", 
                  command=self._restore_selected_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_btn_frame, text="🗑️ Eliminar", 
                  command=self._delete_selected_backup).pack(side=tk.LEFT, padx=5)
        
        # Configurar expansión
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        notebook.add(frame, text="Base de Datos")
        
        # Cargar información inicial
        self._refresh_db_info()
        self._refresh_backup_list()
    
    def _create_action_buttons(self):
        """Crea los botones de acción en la parte inferior"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Aplicar", 
                  command=self._apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Guardar", 
                  command=self._save_settings, 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Restaurar Valores", 
                  command=self._restore_defaults).pack(side=tk.LEFT)
    
    def _bind_events(self):
        """Configura eventos del treeview"""
        self.backup_tree.bind('<<TreeviewSelect>>', self._on_backup_select)
        self.backup_tree.bind('<Double-Button-1>', self._on_backup_double_click)
    
    def _on_backup_select(self, event):
        """Maneja la selección de un backup"""
        selection = self.backup_tree.selection()
        if selection:
            item = selection[0]
            self.selected_backup_path = Path(self.backup_tree.item(item, "tags")[0])
    
    def _on_backup_double_click(self, event):
        """Maneja doble clic en backup"""
        self._restore_selected_backup()
    
    def _update_info_text(self, text: str):
        """Actualiza el texto de información"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)
    
    def _refresh_db_info(self):
        """Actualiza la información de la base de datos"""
        if not self.database_service:
            self._update_info_text("Servicio de base de datos no disponible")
            return
        
        try:
            info = self.database_service.get_database_info()
            
            if info['exists']:
                text = (f"📊 INFORMACIÓN DE BASE DE DATOS\n"
                       f"{'='*40}\n"
                       f"• Ubicación: {info['path']}\n"
                       f"• Tamaño: {info.get('size_mb', 0)} MB\n"
                       f"• Tablas: {info.get('table_count', 0)}\n"
                       f"• Modificado: {info.get('modified', 'N/A')}\n"
                       f"• Backups: {info['backup_count']}\n"
                       f"• Ciclos: {info.get('cycles_count', 0)}\n")
                
                if 'tables' in info:
                    text += f"\n📋 Tablas principales:\n"
                    for table in ['requests', 'cards', 'department', 'users', 'diets', 'diet_liquidations']:
                        if table in info['tables']:
                            text += f"  ✓ {table}\n"
                        else:
                            text += f"  ✗ {table} (no existe)\n"
            else:
                text = f"❌ Base de datos no encontrada en:\n{info['path']}"
            
            self._update_info_text(text)
            
        except Exception as e:
            self._update_info_text(f"Error cargando información:\n{str(e)}")
    
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
                # Determinar tipo
                if "ciclo" in backup_path.stem.lower():
                    backup_type = "Ciclo"
                else:
                    backup_type = "Backup"
                
                # Formatear tamaño
                if size_bytes >= 1024 * 1024:
                    size_str = f"{size_bytes/(1024*1024):.1f} MB"
                elif size_bytes >= 1024:
                    size_str = f"{size_bytes/1024:.1f} KB"
                else:
                    size_str = f"{size_bytes} B"
                
                # Insertar en treeview
                self.backup_tree.insert("", tk.END, values=(
                    backup_date.strftime("%Y-%m-%d %H:%M"),
                    backup_path.name,
                    size_str,
                    backup_type
                ), tags=(str(backup_path),))
            
            # Actualizar contador
            self.backup_tree.heading("Nombre", text=f"Nombre ({len(backups)})")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los backups:\n{str(e)}")
    
    def _perform_backup(self):
        """Realiza backup de la base de datos"""
        if not self.database_service:
            messagebox.showerror("Error", "Servicio de base de datos no disponible")
            return
        
        # Pedir descripción
        description = simpledialog.askstring(
            "Descripción del Backup",
            "Ingrese una descripción para el backup:",
            parent=self
        )
        
        if description is None:  # Usuario canceló
            return
        
        try:
            backup_path = self.database_service.create_backup(description or "manual")
            
            messagebox.showinfo(
                "✅ Backup Exitoso",
                f"Backup creado exitosamente:\n"
                f"• Nombre: {backup_path.name}\n"
                f"• Ubicación: {backup_path.parent}\n\n"
                f"Puede restaurarlo cuando sea necesario."
            )
            
            # Actualizar información
            self._refresh_db_info()
            self._refresh_backup_list()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo crear el backup:\n{str(e)}")
    
    def _restore_selected_backup(self):
        """Restaura el backup seleccionado"""
        if not self.selected_backup_path:
            messagebox.showwarning("Selección", "Por favor, seleccione un backup de la lista")
            return
        
        # Confirmar restauración
        confirm = messagebox.askyesno(
            "⚠️ Confirmar Restauración",
            f"¿Está seguro de restaurar este backup?\n\n"
            f"📄 Archivo: {self.selected_backup_path.name}\n\n"
            f"⚠️ ADVERTENCIA:\n"
            f"1. Se creará un backup de la BD actual\n"
            f"2. La BD actual será sobrescrita\n"
            f"3. La aplicación se CERRARÁ automáticamente\n\n"
            f"¿Continuar con la restauración?"
        )
        
        if not confirm:
            return
        
        try:
            # Mostrar mensaje de bloqueo
            messagebox.showinfo(
                "🔄 Restaurando...",
                f"Restaurando backup: {self.selected_backup_path.name}\n\n"
                f"Por favor, no cierre esta ventana hasta que se complete.\n"
                f"La aplicación se cerrará automáticamente al finalizar."
            )
            
            # Realizar restauración
            success = self.database_service.restore_backup(self.selected_backup_path)
            
            if success:
                # Crear archivo de bloqueo para evitar uso sin reinicio
                lock_file = Path("APP_BLOQUEADA.lock")
                lock_file.write_text(
                    f"La aplicación ha sido restaurada desde un backup.\n"
                    f"Fecha: {datetime.now()}\n"
                    f"Backup: {self.selected_backup_path.name}\n\n"
                    f"Por favor, cierre y reinicie la aplicación completamente."
                )
                
                # Mostrar mensaje final y cerrar aplicación
                messagebox.showinfo(
                    "✅ Restauración Completa",
                    f"Backup restaurado exitosamente.\n\n"
                    f"⚠️ LA APLICACIÓN SE CERRARÁ AHORA\n\n"
                    f"Por favor, ábrala nuevamente manualmente para continuar."
                )
                
                # Forzar cierre de toda la aplicación
                self.master.quit()
            else:
                messagebox.showerror("❌ Error", "No se pudo restaurar el backup")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error restaurando backup:\n{str(e)}")
    
    def _delete_selected_backup(self):
        """Elimina el backup seleccionado"""
        if not self.selected_backup_path:
            messagebox.showwarning("Selección", "Por favor, seleccione un backup de la lista")
            return
        
        confirm = messagebox.askyesno(
            "🗑️ Confirmar Eliminación",
            f"¿Está seguro de eliminar este backup?\n\n"
            f"📄 Archivo: {self.selected_backup_path.name}\n\n"
            f"Esta acción NO se puede deshacer."
        )
        
        if not confirm:
            return
        
        try:
            # Usar el servicio para eliminar
            if hasattr(self.database_service, 'delete_backup'):
                success = self.database_service.delete_backup(self.selected_backup_path)
            else:
                # Eliminación directa si el método no existe
                self.selected_backup_path.unlink()
                success = True
            
            if success:
                messagebox.showinfo("✅ Éxito", "Backup eliminado correctamente")
                self.selected_backup_path = None
                self._refresh_db_info()
                self._refresh_backup_list()
            else:
                messagebox.showerror("❌ Error", "No se pudo eliminar el backup")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error eliminando backup:\n{str(e)}")
    
    def _optimize_database(self):
        """Optimiza la base de datos"""
        if not self.database_service:
            return
        
        confirm = messagebox.askyesno(
            "⚙️ Optimizar Base de Datos",
            "¿Desea optimizar la base de datos?\n\n"
            "Esto mejorará el rendimiento y reducirá el tamaño.\n"
            "Puede tomar unos segundos dependiendo del tamaño."
        )
        
        if not confirm:
            return
        
        try:
            success = self.database_service.optimize_database()
            
            if success:
                messagebox.showinfo("✅ Éxito", "Base de datos optimizada correctamente")
                self._refresh_db_info()
            else:
                messagebox.showerror("❌ Error", "No se pudo optimizar la base de datos")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error optimizando:\n{str(e)}")
    
    def _start_new_cycle(self):
        """Inicia un nuevo ciclo (mejorado)"""
        if not self.database_service:
            messagebox.showerror("Error", "Servicio de base de datos no disponible")
            return
        
        # Pedir nombre del ciclo
        ciclo_nombre = simpledialog.askstring(
            "🆕 Nuevo Ciclo",
            "Ingrese un nombre para el nuevo ciclo:",
            initialvalue=f"Ciclo_{datetime.now().strftime('%Y_%m')}",
            parent=self
        )
        
        if not ciclo_nombre:
            return
        
        # Confirmar
        confirm = messagebox.askyesno(
            "🆕 Confirmar Nuevo Ciclo",
            f"¿Crear nuevo ciclo '{ciclo_nombre}'?\n\n"
            f"✅ SE CONSERVARÁ:\n"
            f"• Solicitantes (requests)\n"
            f"• Tarjetas (cards)\n"
            f"• Departamentos (department)\n"
            f"• Usuarios (users)\n"
            f"• Servicios (diet_services)\n\n"
            f"❌ SE ELIMINARÁ:\n"
            f"• Todas las dietas (diets)\n"
            f"• Todas las liquidaciones (diet_liquidations)\n\n"
            f"⚠️ La aplicación se cerrará automáticamente."
        )
        
        if not confirm:
            return
        
        try:
            # Mostrar progreso
            self.config(cursor="watch")
            self.update()
            
            # Crear nuevo ciclo (esto automáticamente crea backup y restaura)
            new_db_path = self.database_service.create_clean_database_copy(ciclo_nombre)
            
            # Crear archivo de bloqueo
            lock_file = Path("APP_BLOQUEADA.lock")
            lock_file.write_text(
                f"NUEVO CICLO INICIADO\n"
                f"Nombre: {ciclo_nombre}\n"
                f"Fecha: {datetime.now()}\n"
                f"Archivo: {new_db_path.name}\n\n"
                f"Por favor, cierre y reinicie la aplicación."
            )
            
            # Mostrar mensaje final
            messagebox.showinfo(
                "✅ Nuevo Ciclo Creado",
                f"🎉 Nuevo ciclo '{ciclo_nombre}' creado exitosamente!\n\n"
                f"📁 Ubicación: {new_db_path.parent}\n"
                f"📄 Archivo: {new_db_path.name}\n\n"
                f"⚠️ LA APLICACIÓN SE CERRARÁ AHORA\n\n"
                f"Por favor, ábrala nuevamente para comenzar el nuevo ciclo."
            )
            
            # Cerrar aplicación
            self.master.quit()
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo crear el nuevo ciclo:\n{str(e)}")
        finally:
            self.config(cursor="")
    
    def _apply_settings(self):
        """Aplica la configuración sin cerrar"""
        self._save_to_settings_object()
        messagebox.showinfo("✅ Configuración", "Configuración aplicada correctamente")
    
    def _save_settings(self):
        """Guarda la configuración y cierra"""
        self._save_to_settings_object()
        
        if self.settings_service:
            try:
                self.settings_service.save_settings(self.settings)
                messagebox.showinfo("✅ Configuración", "Configuración guardada correctamente")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo guardar:\n{str(e)}")
        
        self.destroy()
    
    def _save_to_settings_object(self):
        """Actualiza el objeto settings con los valores de la UI"""
        self.settings.language = self.language_var.get()
        self.settings.default_currency = self.currency_var.get()
        self.settings.date_format = self.date_format_var.get()
        self.settings.theme = self.theme_var.get()
        self.settings.auto_save = self.auto_save_var.get()
    
    def _restore_defaults(self):
        """Restaura los valores por defecto"""
        if messagebox.askyesno("Restaurar Valores", 
                             "¿Restaurar todos los valores a los predeterminados?"):
            self.settings = AppSettings()
            self._load_settings()
            # Actualizar UI
            self.language_var.set(self.settings.language)
            self.currency_var.set(self.settings.default_currency)
            self.date_format_var.set(self.settings.date_format)
            self.theme_var.set(self.settings.theme)
            self.auto_save_var.set(self.settings.auto_save)