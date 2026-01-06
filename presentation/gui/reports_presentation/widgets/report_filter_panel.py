import tkinter as tk
from tkinter import ttk

class ReportFilterPanel(ttk.LabelFrame):
    """Panel de filtros específicos por tipo de reporte"""
    
    def __init__(self, parent, report_type):
        super().__init__(parent, text="Filtros Avanzados", padding=10)
        self.report_type = report_type
        self._create_filters_by_type()
    
    def _create_filters_by_type(self):
        """Crea filtros según el tipo de reporte"""
        if self.report_type == "tarjetas_caja":
            self._create_card_filters()
        elif self.report_type == "anticipos_sin_liquidar":
            self._create_advance_filters()
        elif self.report_type == "comprobante_contable":
            self._create_accounting_filters()
    
    def _create_card_filters(self):
        """Filtros para reporte de tarjetas"""
        # Filtro por cajero
        ttk.Label(self, text="Cajero:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.cashier_combo = ttk.Combobox(
            self, 
            values=["Todos", "KAREN GUZMAN FIGUEROA", "Otro Cajero"],
            state="readonly",
            width=25
        )
        self.cashier_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.cashier_combo.set("Todos")
        
        # Filtro por saldo mínimo
        ttk.Label(self, text="Saldo Mínimo:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.min_balance = ttk.Entry(self, width=15)
        self.min_balance.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.min_balance.insert(0, "0")
    
    def _create_advance_filters(self):
        """Filtros para reporte de anticipos"""
        # Filtro por días transcurridos
        ttk.Label(self, text="Días transcurridos >:").grid(
            row=0, column=0, sticky='w', padx=5, pady=5
        )
        self.days_entry = ttk.Entry(self, width=10)
        self.days_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Checkbox para mostrar solo vencidos
        self.show_overdue = tk.BooleanVar()
        self.overdue_check = ttk.Checkbutton(
            self, 
            text="Mostrar solo vencidos", 
            variable=self.show_overdue
        )
        self.overdue_check.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=5)
    
    def _create_accounting_filters(self):
        """Filtros para reporte contable"""
        # Filtro por tipo de operación
        ttk.Label(self, text="Tipo Operación:").grid(
            row=0, column=0, sticky='w', padx=5, pady=5
        )
        self.operation_combo = ttk.Combobox(
            self, 
            values=["Todas", "Anticipo", "Liquidación", "Reembolso"],
            state="readonly",
            width=15
        )
        self.operation_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.operation_combo.set("Todas")
        
        # Filtro por cuenta contable
        ttk.Label(self, text="Cuenta:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.account_entry = ttk.Entry(self, width=10)
        self.account_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
    
    def get_filters(self):
        """Devuelve los filtros aplicados"""
        filters = {'report_type': self.report_type}
        
        # Recopilar valores de todos los controles
        for child in self.winfo_children():
            if isinstance(child, ttk.Combobox):
                filters[child._name if hasattr(child, '_name') else 'combobox'] = child.get()
            elif isinstance(child, ttk.Entry):
                filters[child._name if hasattr(child, '_name') else 'entry'] = child.get()
            elif isinstance(child, ttk.Checkbutton):
                var_name = str(child.cget('variable')).replace('PY_VAR', 'var')
                filters[var_name] = child.instate(['selected'])
        
        return filters