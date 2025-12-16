import tkinter as tk
from tkinter import ttk
from typing import Optional
from core.entities.account import Account
from application.services.account_service import AccountService


class AccountFormDialog(tk.Toplevel):
    """Diálogo optimizado para formulario de cuentas"""
    
    def __init__(self, parent, account_service: AccountService, account: Optional[Account] = None):
        super().__init__(parent)
        
        self.account_service = account_service
        self.account = account
        self.result = False
        
        # Configuración de ventana
        self.title("Editar Cuenta" if account else "Nueva Cuenta")
        self.geometry("600x400")
        self.minsize(500, 350)
        self.resizable(True, True)
        
        # Comportamiento modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Configurar layout responsivo
        self._setup_responsive_layout()
        
        # Crear interfaz
        self._create_ui()
        
        # Centrar y enfocar
        self._center_window()
        self._focus_first_field()
        
        # Atajos
        self._setup_shortcuts()
        
    def _setup_responsive_layout(self):
        """Configurar pesos responsivos"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    def _create_ui(self):
        """Crear interfaz del formulario"""
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_text = "✏️ Editar Cuenta" if self.account else "➕ Nueva Cuenta"
        title = ttk.Label(
            main_frame,
            text=title_text,
            font=('Segoe UI', 12, 'bold')
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Campo: Número de cuenta
        ttk.Label(
            form_frame,
            text="Número/Código:",
            font=('Segoe UI', 10)
        ).grid(row=0, column=0, sticky="w", pady=10, padx=(0, 10))
        
        self._account_var = tk.StringVar()
        self._account_entry = ttk.Entry(
            form_frame,
            textvariable=self._account_var,
            font=('Segoe UI', 10)
        )
        
        if self.account:
            self._account_var.set(self.account.account)
            self._account_entry.config(state='readonly')
            
        self._account_entry.grid(row=0, column=1, sticky="ew", pady=10)
        
        # Campo: Descripción
        ttk.Label(
            form_frame,
            text="Descripción:",
            font=('Segoe UI', 10)
        ).grid(row=1, column=0, sticky="nw", pady=10, padx=(0, 10))
        
        # Frame para área de texto con scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Área de texto con scroll
        self._description_text = tk.Text(
            text_frame,
            font=('Segoe UI', 10),
            wrap=tk.WORD,
            height=8
        )
        
        scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self._description_text.yview
        )
        self._description_text.configure(yscrollcommand=scrollbar.set)
        
        self._description_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        if self.account and self.account.description:
            self._description_text.insert('1.0', self.account.description)
            
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self._on_cancel,
            width=12
        ).grid(row=0, column=0, padx=(0, 5), sticky="e")
        
        save_text = "💾 Guardar" if not self.account else "💾 Actualizar"
        ttk.Button(
            button_frame,
            text=save_text,
            command=self._save_account,
            style='success.TButton',
            width=12
        ).grid(row=0, column=1, padx=(5, 0), sticky="w")
        
    def _center_window(self):
        """Centrar ventana"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _focus_first_field(self):
        """Enfocar el primer campo apropiado"""
        if self.account:
            self._description_text.focus_set()
        else:
            self._account_entry.focus_set()
            
    def _setup_shortcuts(self):
        """Configurar atajos de teclado"""
        self.bind('<Escape>', lambda e: self._on_cancel())
        self.bind('<Control-s>', lambda e: self._save_account())
        self.bind('<Return>', lambda e: self._save_account())
        
    def _on_cancel(self):
        """Cancelar y cerrar"""
        self.grab_release()
        self.destroy()
        
    def _save_account(self):
        """Guardar la cuenta"""
        account_number = self._account_var.get().strip()
        description = self._description_text.get('1.0', tk.END).strip()
        
        # Validaciones básicas
        if not account_number:
            tk.messagebox.showerror("Error", "El número de cuenta es requerido")
            self._account_entry.focus_set()
            return
            
        try:
            if self.account:
                # Actualizar cuenta existente
                if hasattr(self.account, 'id') and self.account.id:
                    updated = self.account_service.update_account(
                        self.account.id,
                        account_number,
                        description
                    )
                    
                    if updated:
                        self.result = True
                        self._on_cancel()
                    else:
                        tk.messagebox.showerror("Error", "No se pudo actualizar")
            else:
                # Crear nueva cuenta
                new_account = self.account_service.create_account(
                    account_number,
                    description
                )
                
                if new_account:
                    self.result = True
                    self._on_cancel()
                else:
                    tk.messagebox.showerror("Error", "No se pudo crear la cuenta")
                    
        except ValueError as e:
            tk.messagebox.showerror("Validación", str(e))
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error al guardar: {str(e)}")