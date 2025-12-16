import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
from core.entities.account import Account


class AccountListWidget(ttk.Frame):
    """Widget para mostrar lista de cuentas con acciones"""
    
    def __init__(self, parent, account_service, on_edit: Callable, on_delete: Callable):
        super().__init__(parent)
        
        self.account_service = account_service
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.accounts = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crear la interfaz del widget"""
        # Frame principal con scroll
        self.canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de scroll con ratón
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Frame para encabezados
        self.header_frame = ttk.Frame(self.scrollable_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Encabezados de columnas
        ttk.Label(
            self.header_frame, 
            text="Número/Código", 
            font=('Arial', 10, 'bold'),
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            self.header_frame, 
            text="Descripción", 
            font=('Arial', 10, 'bold'),
            width=50
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            self.header_frame, 
            text="Acciones", 
            font=('Arial', 10, 'bold'),
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _on_mousewheel(self, event):
        """Manejar scroll del ratón"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_accounts(self, accounts: List[Account]):
        """Cargar y mostrar lista de cuentas"""
        self.accounts = accounts
        
        # Limpiar lista actual (excepto encabezados)
        for widget in self.scrollable_frame.winfo_children()[1:]:
            widget.destroy()
        
        if not accounts:
            # Mostrar mensaje si no hay cuentas
            no_data_frame = ttk.Frame(self.scrollable_frame)
            no_data_frame.pack(fill=tk.X, pady=50)
            
            ttk.Label(
                no_data_frame, 
                text="No hay cuentas registradas", 
                font=('Arial', 12),
                foreground='gray'
            ).pack()
            return
        
        # Mostrar cada cuenta
        for idx, account in enumerate(accounts):
            self._create_account_row(account, idx)
    
    def _create_account_row(self, account: Account, index: int):
        """Crear una fila para una cuenta"""
        # Determinar estilo según índice
        style_name = 'EvenRow.TFrame' if index % 2 == 0 else 'OddRow.TFrame'
        
        row_frame = ttk.Frame(self.scrollable_frame, style=style_name)
        row_frame.pack(fill=tk.X, pady=1, padx=2)
        
        # Número de cuenta
        account_label = ttk.Label(
            row_frame, 
            text=account.account, 
            width=20,
            anchor="w"
        )
        account_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Descripción (con tooltip si es largo)
        description = account.description if account.description else "(Sin descripción)"
        desc_label = ttk.Label(
            row_frame, 
            text=description, 
            width=50,
            anchor="w"
        )
        desc_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Crear tooltip si la descripción es larga
        if len(description) > 60:
            self._create_tooltip(desc_label, description)
        
        # Frame para botones de acción
        actions_frame = ttk.Frame(row_frame)
        actions_frame.pack(side=tk.LEFT, padx=5)
        
        # Botón Editar
        edit_btn = ttk.Button(
            actions_frame,
            text="✏️ Editar",
            command=lambda acc=account: self.on_edit(acc),
            width=10
        )
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Botón Eliminar
        delete_btn = ttk.Button(
            actions_frame,
            text="🗑️ Eliminar",
            command=lambda acc=account: self.on_delete(acc),
            width=10,
            style='Delete.TButton'
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
    
    def _create_tooltip(self, widget, text):
        """Crear tooltip para texto largo"""
        def on_enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(
                tooltip, 
                text=text, 
                background="#ffffe0",
                relief="solid", 
                borderwidth=1,
                padding=5,
                wraplength=300
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)