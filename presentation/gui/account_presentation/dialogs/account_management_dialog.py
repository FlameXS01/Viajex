import tkinter as tk
from tkinter import ttk
from typing import List
from core.entities.account import Account
from application.services.account_service import AccountService
from presentation.gui.account_presentation.dialogs.account_form_dialog import AccountFormDialog


class AccountManagementDialog(tk.Toplevel):
    """Diálogo optimizado para gestión de cuentas"""
    
    def __init__(self, parent, account_service: AccountService):
        super().__init__(parent)
        
        self.account_service = account_service
        self.parent = parent
        self._filtered_accounts = []
        
        # Configuración de ventana
        self.title("Gestión de Cuentas")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.resizable(False, False)
        
        # Comportamiento modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Variables de estado
        self._search_var = tk.StringVar()
        
        # Configurar layout responsivo
        self._setup_responsive_layout()
        
        # Crear interfaz
        self._create_ui()
        
        # Cargar datos
        self._load_accounts()
        
        # Centrar y enfocar
        self._center_window()
        self.focus_force()
        
        # Atajos
        self._setup_shortcuts()
        
    def _setup_responsive_layout(self):
        """Configurar pesos para responsividad"""
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    def _create_ui(self):
        """Crear interfaz optimizada"""
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self._create_header(main_frame)
        
        # Barra de herramientas
        self._create_toolbar(main_frame)
        
        # Lista de cuentas (Treeview para mejor rendimiento)
        self._create_accounts_table(main_frame)
        
        # Barra de estado
        self._create_status_bar(main_frame)
        
    def _create_header(self, parent):
        """Crear cabecera"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(
            header_frame,
            text="📊 Gestión de Cuentas",
            font=('Segoe UI', 14, 'bold')
        ).grid(row=0, column=0, sticky="w")
        
        ttk.Button(
            header_frame,
            text="Cerrar",
            command=self._on_close,
            width=8
        ).grid(row=0, column=2, sticky="e")
        
    def _create_toolbar(self, parent):
        """Crear barra de herramientas"""
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Buscador
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self._search_var.trace('w', lambda *args: self._filter_accounts())
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self._search_var,
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botones de acción
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side=tk.RIGHT)
        
        actions = [
            ("➕ Nueva", self._add_account, 'success.TButton'),
            ("✏️ Editar", self._edit_selected, 'info.TButton'),
            ("🗑️ Eliminar", self._delete_selected, 'danger.TButton'),
            ("🔄 Actualizar", self._load_accounts, ''),
            ("📊 Resumen", self._show_summary, '')
        ]
        
        for text, command, style in actions:
            ttk.Button(
                action_frame,
                text=text,
                command=command,
                style=style if style else '',
                width=12
            ).pack(side=tk.LEFT, padx=2)
        
    def _create_accounts_table(self, parent):
        """Crear tabla de cuentas usando Treeview para mejor rendimiento"""
        # Frame contenedor
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview con scrollbars
        columns = ('account', 'description')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            height=27
        )
        
        # Configurar columnas
        self.tree.heading('account', text='Número/Código', anchor='w')
        self.tree.heading('description', text='Descripción', anchor='w')
        
        self.tree.column('account', width=150, minwidth=100)
        self.tree.column('description', width=600, minwidth=200)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew", columnspan=2)
        
        # Bind events
        self.tree.bind('<Double-Button-1>', lambda e: self._edit_selected())
        self.tree.bind('<Delete>', lambda e: self._delete_selected())
        
    def _create_status_bar(self, parent):
        """Crear barra de estado"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN)
        status_frame.grid(row=3, column=0, sticky="ew")
        
        self._status_label = ttk.Label(
            status_frame,
            text="Listo",
            font=('Segoe UI', 9)
        )
        self._status_label.pack(side=tk.LEFT, padx=5)
        
        self._stats_label = ttk.Label(
            status_frame,
            text="Cargando...",
            font=('Segoe UI', 9)
        )
        self._stats_label.pack(side=tk.RIGHT, padx=5)
        
    def _center_window(self):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _setup_shortcuts(self):
        """Configurar atajos de teclado"""
        self.bind('<Escape>', lambda e: self._on_close())
        self.bind('<F5>', lambda e: self._load_accounts())
        self.bind('<Control-n>', lambda e: self._add_account())
        self.bind('<Control-f>', lambda e: self.focus_set())
        
    def _on_close(self):
        """Manejar cierre de ventana"""
        self.grab_release()
        self.destroy()
        
    def _load_accounts(self):
        """Cargar cuentas de forma optimizada"""
        try:
            self._set_status("Cargando cuentas...")
            
            accounts = self.account_service.get_all_accounts()
            self._filtered_accounts = accounts
            
            # Limpiar tabla
            self.tree.delete(*self.tree.get_children())
            
            # Insertar datos
            for account in accounts:
                self.tree.insert(
                    '', 
                    tk.END, 
                    values=(
                        account.account,
                        account.description or "(Sin descripción)"
                    ),
                    tags=('odd' if len(self.tree.get_children()) % 2 else 'even',)
                )
            
            # Aplicar estilos de filas alternadas
            self.tree.tag_configure('odd', background='#f9f9f9')
            self.tree.tag_configure('even', background='white')
            
            self._update_stats(accounts)
            self._set_status(f"Cargadas {len(accounts)} cuentas")
            
        except Exception as e:
            self._set_status(f"Error: {str(e)}", True)
            
    def _set_status(self, message: str, error: bool = False):
        """Actualizar barra de estado"""
        color = "red" if error else "black"
        self._status_label.config(text=message, foreground=color)
        
    def _update_stats(self, accounts: List[Account]):
        """Actualizar estadísticas"""
        total = len(accounts)
        with_desc = sum(1 for acc in accounts if acc.description and acc.description.strip())
        
        self._stats_label.config(
            text=f"Total: {total} | Con descripción: {with_desc} ({with_desc/total*100:.0f}%)"
        )
        
    def _get_selected_account(self):
        """Obtener cuenta seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return None
            
        item = self.tree.item(selection[0])
        account_number = item['values'][0]
        
        # Buscar en las cuentas filtradas
        for account in self._filtered_accounts:
            if account.account == account_number:
                return account
        return None
        
    def _add_account(self):
        """Abrir diálogo para nueva cuenta"""
        dialog = AccountFormDialog(self, self.account_service)
        self.wait_window(dialog)
        
        if dialog.result:
            self._load_accounts()
            
    def _edit_selected(self):
        """Editar cuenta seleccionada"""
        account = self._get_selected_account()
        if not account:
            tk.messagebox.showwarning("Selección", "Por favor seleccione una cuenta")
            return
            
        dialog = AccountFormDialog(self, self.account_service, account)
        self.wait_window(dialog)
        
        if dialog.result:
            self._load_accounts()
            
    def _delete_selected(self):
        """Eliminar cuenta seleccionada"""
        account = self._get_selected_account()
        if not account:
            tk.messagebox.showwarning("Selección", "Por favor seleccione una cuenta")
            return
            
        from presentation.gui.user_presentation.dialogs.confirm_dialog import ConfirmDialog
        
        def delete_confirmed():
            try:
                if hasattr(account, 'id') and account.id:
                    success = self.account_service.delete_account(account.id)
                    if success:
                        self._set_status(f"Cuenta '{account.account}' eliminada")
                        self._load_accounts()
                    else:
                        self._set_status("No se pudo eliminar la cuenta", True)
                else:
                    self._set_status("ID de cuenta inválido", True)
            except Exception as e:
                error_msg = str(e)
                if "integridad" in error_msg.lower() or "foreign key" in error_msg.lower():
                    tk.messagebox.showerror(
                        "Error",
                        f"La cuenta '{account.account}' está siendo utilizada"
                    )
                else:
                    tk.messagebox.showerror("Error", f"Error: {error_msg}")
                    
        ConfirmDialog(
            self,
            title="Confirmar Eliminación",
            message=f"¿Eliminar cuenta '{account.account}'?",
            confirm_callback=delete_confirmed
        )
        
    def _filter_accounts(self):
        """Filtrar cuentas en tiempo real"""
        search_text = self._search_var.get().lower()
        
        if not search_text:
            self._load_accounts()
            return
            
        filtered = [
            acc for acc in self._filtered_accounts
            if search_text in acc.account.lower() or 
               (acc.description and search_text in acc.description.lower())
        ]
        
        # Actualizar tabla
        self.tree.delete(*self.tree.get_children())
        for account in filtered:
            self.tree.insert(
                '', 
                tk.END, 
                values=(
                    account.account,
                    account.description or "(Sin descripción)"
                )
            )
            
        self._update_stats(filtered)
        self._set_status(f"Encontradas {len(filtered)} cuentas")
        
    def _show_summary(self):
        """Mostrar resumen"""
        try:
            summary = self.account_service.get_accounts_summary()
            
            summary_text = (
                f"📊 RESUMEN DE CUENTAS\n\n"
                f"• Total: {summary['total_accounts']}\n"
                f"• Con descripción: {summary['accounts_with_description']}\n"
                f"• Cobertura: {summary['description_coverage_percentage']:.1f}%\n\n"
                f"📁 Distribución por prefijos:\n"
            )
            
            for prefix, count in sorted(summary['accounts_by_prefix'].items()):
                summary_text += f"  {prefix}: {count}\n"
                
            tk.messagebox.showinfo("Resumen", summary_text)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error: {str(e)}")