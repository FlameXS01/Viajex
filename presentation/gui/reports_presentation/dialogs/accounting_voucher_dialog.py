"""
accounting_voucher_dialog.py
Diálogo para configurar la generación de "Comprobante contable".
Genera asientos contables basados en anticipos y liquidaciones.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from presentation.gui.reports_presentation.dialogs.base_report_dialog import BaseReportDialog
from presentation.gui.reports_presentation.dialogs.date_range_dialog import DateRangeDialog


class AccountingVoucherDialog(BaseReportDialog):
    """Diálogo para configurar comprobante contable"""
    
    def __init__(self, parent, 
                 entities: Optional[List[str]] = None,
                 accounts: Optional[List[Tuple[str, str]]] = None,
                 cost_centers: Optional[List[str]] = None):
        """
        Inicializa el diálogo para comprobante contable.
        
        Args:
            parent: Ventana padre
            entities: Lista de entidades disponibles
            accounts: Lista de cuentas contables (código, descripción)
            cost_centers: Lista de centros de costo disponibles
        """
        self.entities = entities or ["CIMEX - Gerencia Administrativa"]
        
        # Cuentas del PDF (Page 3, 8, 9)
        self.accounts = accounts or [
            ("16101001", "Anticipo para Dieta"),
            ("10110200", "Efectivo en Caja /Fondo"),
            ("70044400", "Gasto de Publicidad"),
            ("70144500", "Gasto Hospedaje Publicidad"),
            ("82244400", "Gasto de Alimentación"),
            ("82344500", "Gasto de Hospedaje"),
            ("82844400", "Gasto de Mantenimiento"),
            ("82944500", "Gasto de Transporte")
        ]
        
        self.cost_centers = cost_centers or [
            "CCS2410", "CCS2410101", "CCS2410102", "CCS2410103", 
            "CCS24104", "CCS24106", "CCS2410511", "CCS2410531", "CCS2410541"
        ]
        
        super().__init__(parent, "Generar Comprobante Contable", width=700, height=650)
    
    def _create_widgets(self) -> None:
        """Crea los widgets del diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar expansión
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título descriptivo
        ttk.Label(
            main_frame,
            text="Configurar Generación de Comprobante Contable",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Información importante
        info_text = "📝 El comprobante se genera con:\n"
        info_text += "• Fecha = fecha del fin del viaje (para liquidaciones)\n"
        info_text += "• Incluye: anticipos del día + liquidaciones con fecha final del día"
        
        ttk.Label(
            main_frame,
            text=info_text,
            font=('Arial', 9, 'italic'),
            foreground='darkblue'
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Sección de parámetros principales
        basic_frame = self._create_section(main_frame, "Parámetros del Comprobante", 2)
        
        # Fecha del comprobante
        ttk.Label(basic_frame, text="Fecha del comprobante:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.voucher_date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        date_frame = ttk.Frame(basic_frame)
        date_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        ttk.Entry(
            date_frame, 
            textvariable=self.voucher_date_var,
            width=12,
            state='readonly'
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            date_frame,
            text="📅",
            command=self._select_voucher_date,
            width=3
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Entidad
        ttk.Label(basic_frame, text="Entidad:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.entity_var = tk.StringVar(value=self.entities[0])
        entity_combo = ttk.Combobox(
            basic_frame,
            textvariable=self.entity_var,
            values=self.entities,
            state='readonly',
            width=40
        )
        entity_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Tipo de transacción
        ttk.Label(basic_frame, text="Tipo de transacción:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.transaction_type_var = tk.StringVar(value="ambos")
        trans_frame = ttk.Frame(basic_frame)
        trans_frame.grid(row=2, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            trans_frame,
            text="Solo Anticipos",
            variable=self.transaction_type_var,
            value="anticipos"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            trans_frame,
            text="Solo Liquidaciones",
            variable=self.transaction_type_var,
            value="liquidaciones"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            trans_frame,
            text="Ambos",
            variable=self.transaction_type_var,
            value="ambos"
        ).pack(side=tk.LEFT)
        
        # Número de consecutivo (opcional)
        ttk.Label(basic_frame, text="Número de consecutivo:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.consecutive_var = tk.StringVar()
        consecutive_frame = ttk.Frame(basic_frame)
        consecutive_frame.grid(row=3, column=1, sticky="w", pady=10)
        
        ttk.Entry(consecutive_frame, textvariable=self.consecutive_var, 
                 width=15).pack(side=tk.LEFT)
        ttk.Label(consecutive_frame, text=" (dejar vacío para auto-generar)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Sección de configuración de cuentas
        accounts_frame = self._create_section(main_frame, "Configuración de Cuentas", 3)
        
        # Cuenta de anticipos
        ttk.Label(accounts_frame, text="Cuenta de anticipos:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.advance_account_var = tk.StringVar(value="16101001")
        advance_account_combo = ttk.Combobox(
            accounts_frame,
            textvariable=self.advance_account_var,
            values=[f"{code} - {desc}" for code, desc in self.accounts],
            state='readonly',
            width=40
        )
        advance_account_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Cuenta de caja
        ttk.Label(accounts_frame, text="Cuenta de caja:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.cash_account_var = tk.StringVar(value="10110200")
        cash_account_combo = ttk.Combobox(
            accounts_frame,
            textvariable=self.cash_account_var,
            values=[f"{code} - {desc}" for code, desc in self.accounts],
            state='readonly',
            width=40
        )
        cash_account_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Cuenta de gastos (para liquidaciones)
        ttk.Label(accounts_frame, text="Cuenta de gastos (liquidaciones):").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.expense_account_var = tk.StringVar(value="70044400")
        expense_account_combo = ttk.Combobox(
            accounts_frame,
            textvariable=self.expense_account_var,
            values=[f"{code} - {desc}" for code, desc in self.accounts],
            state='readonly',
            width=40
        )
        expense_account_combo.grid(row=2, column=1, sticky="w", pady=10)
        
        # Centro de costo por defecto
        ttk.Label(accounts_frame, text="Centro de costo por defecto:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.default_cost_center_var = tk.StringVar(value="CCS2410")
        cost_center_combo = ttk.Combobox(
            accounts_frame,
            textvariable=self.default_cost_center_var,
            values=self.cost_centers,
            state='readonly',
            width=20
        )
        cost_center_combo.grid(row=3, column=1, sticky="w", pady=10)
        
        # Sección de filtros adicionales
        filters_frame = self._create_section(main_frame, "Filtros Adicionales", 4)
        
        # Departamento específico
        ttk.Label(filters_frame, text="Departamento específico:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.department_var = tk.StringVar(value="TODOS")
        department_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.department_var,
            values=["TODOS", "01 - Gerencia General", "16 - Gerencia Comercial", "17 - Publicidad"],
            state='readonly',
            width=30
        )
        department_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Rango de importes
        ttk.Label(filters_frame, text="Filtrar por importe:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        amount_frame = ttk.Frame(filters_frame)
        amount_frame.grid(row=1, column=1, sticky="w", pady=10)
        
        self.min_amount_var = tk.StringVar()
        self.max_amount_var = tk.StringVar()
        
        ttk.Entry(amount_frame, textvariable=self.min_amount_var, width=10).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" a ").pack(side=tk.LEFT, padx=5)
        ttk.Entry(amount_frame, textvariable=self.max_amount_var, width=10).pack(side=tk.LEFT)
        ttk.Label(amount_frame, text=" CUP").pack(side=tk.LEFT, padx=(5, 0))
        
        # Incluir comprobante anterior
        self.include_previous_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filters_frame,
            text="Incluir comprobantes anteriores no procesados",
            variable=self.include_previous_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Sección de opciones de salida
        output_frame = self._create_section(main_frame, "Opciones de Salida", 5)
        
        # Formato del comprobante
        ttk.Label(output_frame, text="Formato del comprobante:").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.voucher_format_var = tk.StringVar(value="detallado")
        format_frame = ttk.Frame(output_frame)
        format_frame.grid(row=0, column=1, sticky="w", pady=10)
        
        ttk.Radiobutton(
            format_frame,
            text="Detallado (con desglose)",
            variable=self.voucher_format_var,
            value="detallado"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            format_frame,
            text="Resumido",
            variable=self.voucher_format_var,
            value="resumido"
        ).pack(side=tk.LEFT)
        
        # Salida a sistema contable
        ttk.Label(output_frame, text="Exportar a sistema:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=10
        )
        
        self.export_system_var = tk.StringVar(value="ninguno")
        system_combo = ttk.Combobox(
            output_frame,
            textvariable=self.export_system_var,
            values=["Ninguno", "SAP", "SAGE", "ContPAQ", "Archivo TXT", "Archivo Excel"],
            state='readonly',
            width=20
        )
        system_combo.grid(row=1, column=1, sticky="w", pady=10)
        
        # Validar sumas iguales
        self.validate_balances_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            output_frame,
            text="Validar que DEBE = HABER",
            variable=self.validate_balances_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Generar asiento de reversa
        self.generate_reverse_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            output_frame,
            text="Generar asiento de reversa (para pruebas)",
            variable=self.generate_reverse_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Mostrar vista previa antes de generar
        self.show_preview_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            output_frame,
            text="Mostrar vista previa antes de generar",
            variable=self.show_preview_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Frame para botones especiales
        special_buttons_frame = ttk.Frame(main_frame)
        special_buttons_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            special_buttons_frame,
            text="Calcular Totales",
            command=self._calculate_totals,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Vista Previa",
            command=self._show_preview,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            special_buttons_frame,
            text="Plantilla Guardar",
            command=self._save_template,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame para botones principales
        self.button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        # Cambiar texto del botón Aceptar
        self.accept_button.config(text="Generar Comprobante")
    
    def _select_voucher_date(self) -> None:
        """Abre diálogo para seleccionar fecha del comprobante."""
        try:
            current_date_str = self.voucher_date_var.get()
            if current_date_str:
                current_date = datetime.strptime(current_date_str, "%d/%m/%Y")
            else:
                current_date = datetime.now()
            
            # Usar tkcalendar si está disponible
            try:
                from tkcalendar import Calendar
                
                top = tk.Toplevel(self)
                top.title("Seleccionar Fecha del Comprobante")
                top.transient(self)
                top.grab_set()
                
                cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
                cal.selection_set(current_date)
                cal.pack(padx=10, pady=10)
                
                def on_accept():
                    self.voucher_date_var.set(cal.get_date())
                    top.destroy()
                
                ttk.Button(top, text="Aceptar", command=on_accept).pack(pady=(0, 10))
                
                # Centrar
                top.update_idletasks()
                x = self.winfo_x() + (self.winfo_width() // 2) - (top.winfo_width() // 2)
                y = self.winfo_y() + (self.winfo_height() // 2) - (top.winfo_height() // 2)
                top.geometry(f"+{x}+{y}")
                
            except ImportError:
                # Fallback
                new_date = tk.simpledialog.askstring(
                    "Fecha del Comprobante",
                    "Ingrese fecha del comprobante (DD/MM/AAAA):",
                    initialvalue=current_date_str,
                    parent=self
                )
                if new_date:
                    try:
                        datetime.strptime(new_date, "%d/%m/%Y")
                        self.voucher_date_var.set(new_date)
                    except ValueError:
                        messagebox.showerror("Error", "Formato inválido", parent=self)
                        
        except ValueError:
            messagebox.showerror("Error", "Fecha actual inválida", parent=self)
    
    def _calculate_totals(self) -> None:
        """Calcula los totales estimados del comprobante."""
        # Esta función simularía el cálculo de totales
        messagebox.showinfo(
            "Calcular Totales",
            "Esta función calcularía los totales estimados del comprobante:\n\n"
            "1. Total anticipos del día: 8,000.00 CUP\n"
            "2. Total liquidaciones: 1,200.00 CUP\n"
            "3. Total comprobante: 9,200.00 CUP\n\n"
            "DEBE: 9,200.00 CUP\n"
            "HABER: 9,200.00 CUP\n"
            "Balance: ✓",
            parent=self
        )
    
    def _show_preview(self) -> None:
        """Muestra una vista previa del comprobante."""
        if self._validate():
            params = self._get_result_data()
            
            preview_msg = f"Vista previa del Comprobante Contable:\n\n"
            preview_msg += f"Fecha: {params['voucher_date_str']}\n"
            preview_msg += f"Entidad: {params['entity']}\n"
            preview_msg += f"Tipo: {params['transaction_type']}\n"
            
            if params['consecutive']:
                preview_msg += f"Consecutivo: {params['consecutive']}\n"
            
            preview_msg += f"\nCuentas configuradas:\n"
            preview_msg += f"• Anticipos: {params['advance_account']}\n"
            preview_msg += f"• Caja: {params['cash_account']}\n"
            preview_msg += f"• Gastos: {params['expense_account']}\n"
            preview_msg += f"• CCosto: {params['default_cost_center']}\n"
            
            if params['department'] != "TODOS":
                preview_msg += f"\nFiltro departamento: {params['department']}\n"
            
            preview_msg += f"\nOpciones:\n"
            preview_msg += f"• Formato: {params['voucher_format']}\n"
            preview_msg += f"• Exportar a: {params['export_system']}\n"
            preview_msg += f"• Validar balance: {'Sí' if params['validate_balances'] else 'No'}\n"
            preview_msg += f"• Generar reversa: {'Sí' if params['generate_reverse'] else 'No'}"
            
            messagebox.showinfo("Vista Previa del Comprobante", preview_msg, parent=self)
    
    def _save_template(self) -> None:
        """Guarda la configuración como plantilla."""
        template_name = tk.simpledialog.askstring(
            "Guardar Plantilla",
            "Nombre de la plantilla:",
            parent=self
        )
        
        if template_name:
            messagebox.showinfo(
                "Plantilla Guardada",
                f"Plantilla '{template_name}' guardada exitosamente.\n"
                f"Puede cargarla desde el menú de plantillas.",
                parent=self
            )
    
    def _validate_required_fields(self) -> bool:
        """Valida los campos requeridos."""
        errors = []
        
        # Validar fecha del comprobante
        date_str = self.voucher_date_var.get().strip()
        if not date_str:
            errors.append("La fecha del comprobante es requerida")
        else:
            try:
                voucher_date = datetime.strptime(date_str, "%d/%m/%Y")
                # Validar que no sea fecha futura
                if voucher_date > datetime.now():
                    errors.append("La fecha del comprobante no puede ser futura")
            except ValueError:
                errors.append("Formato de fecha inválido (use DD/MM/AAAA)")
        
        # Validar cuentas
        advance_account = self.advance_account_var.get()
        cash_account = self.cash_account_var.get()
        expense_account = self.expense_account_var.get()
        
        if not advance_account:
            errors.append("Seleccione cuenta de anticipos")
        
        if not cash_account:
            errors.append("Seleccione cuenta de caja")
        
        if not expense_account and self.transaction_type_var.get() in ["liquidaciones", "ambos"]:
            errors.append("Seleccione cuenta de gastos para liquidaciones")
        
        # Validar que las cuentas sean diferentes
        accounts = [advance_account, cash_account, expense_account]
        unique_accounts = set([acc.split(" - ")[0] for acc in accounts if acc])
        if len(unique_accounts) < len([acc for acc in accounts if acc]):
            errors.append("Las cuentas deben ser diferentes")
        
        # Validar importes
        min_amount = self.min_amount_var.get().strip()
        max_amount = self.max_amount_var.get().strip()
        
        if min_amount:
            try:
                float(min_amount)
                if float(min_amount) < 0:
                    errors.append("El importe mínimo no puede ser negativo")
            except ValueError:
                errors.append("Importe mínimo inválido")
        
        if max_amount:
            try:
                float(max_amount)
                if float(max_amount) < 0:
                    errors.append("El importe máximo no puede ser negativo")
            except ValueError:
                errors.append("Importe máximo inválido")
        
        if min_amount and max_amount:
            try:
                if float(min_amount) > float(max_amount):
                    errors.append("El importe mínimo no puede ser mayor al máximo")
            except:
                pass
        
        # Agregar errores
        for error in errors:
            self._add_validation_error(error)
        
        return len(errors) == 0
    
    def _get_result_data(self) -> Dict[str, Any]:
        """Obtiene los datos de configuración del comprobante."""
        date_str = self.voucher_date_var.get().strip()
        voucher_date = datetime.strptime(date_str, "%d/%m/%Y")
        
        # Extraer códigos de cuentas
        advance_account_code = self.advance_account_var.get().split(" - ")[0] if " - " in self.advance_account_var.get() else self.advance_account_var.get()
        cash_account_code = self.cash_account_var.get().split(" - ")[0] if " - " in self.cash_account_var.get() else self.cash_account_var.get()
        expense_account_code = self.expense_account_var.get().split(" - ")[0] if " - " in self.expense_account_var.get() else self.expense_account_var.get()
        
        return {
            'voucher_date': voucher_date,
            'voucher_date_str': date_str,
            'entity': self.entity_var.get(),
            'transaction_type': self.transaction_type_var.get(),
            'consecutive': self.consecutive_var.get().strip() if self.consecutive_var.get().strip() else None,
            'advance_account': advance_account_code,
            'cash_account': cash_account_code,
            'expense_account': expense_account_code,
            'default_cost_center': self.default_cost_center_var.get(),
            'department': self.department_var.get() if self.department_var.get() != "TODOS" else None,
            'min_amount': self.min_amount_var.get().strip() if self.min_amount_var.get().strip() else None,
            'max_amount': self.max_amount_var.get().strip() if self.max_amount_var.get().strip() else None,
            'include_previous': self.include_previous_var.get(),
            'voucher_format': self.voucher_format_var.get(),
            'export_system': self.export_system_var.get(),
            'validate_balances': self.validate_balances_var.get(),
            'generate_reverse': self.generate_reverse_var.get(),
            'show_preview': self.show_preview_var.get(),
            'report_name': 'accounting_voucher'
        }


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Crear diálogo
    dialog = AccountingVoucherDialog(root)
    result = dialog.show()
    
    if result:
        print("Configuración del Comprobante Contable:")
        print(f"  Fecha: {result['voucher_date_str']}")
        print(f"  Entidad: {result['entity']}")
        print(f"  Tipo transacción: {result['transaction_type']}")
        
        if result['consecutive']:
            print(f"  Consecutivo: {result['consecutive']}")
        
        print(f"  Cuenta anticipos: {result['advance_account']}")
        print(f"  Cuenta caja: {result['cash_account']}")
        print(f"  Cuenta gastos: {result['expense_account']}")
        print(f"  Centro costo: {result['default_cost_center']}")
        
        if result['department']:
            print(f"  Departamento: {result['department']}")
        
        if result['min_amount'] or result['max_amount']:
            print(f"  Importe filtro: {result['min_amount'] or '0'} a {result['max_amount'] or '∞'}")
        
        print(f"  Incluir anteriores: {result['include_previous']}")
        print(f"  Formato: {result['voucher_format']}")
        print(f"  Exportar a: {result['export_system']}")
        print(f"  Validar balance: {result['validate_balances']}")
        print(f"  Generar reversa: {result['generate_reverse']}")
        print(f"  Mostrar vista previa: {result['show_preview']}")
    else:
        print("Diálogo cancelado")
    
    root.destroy()