import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class ReportParams(ttk.LabelFrame):
    """Panel de parámetros para filtrar reportes"""
    
    def __init__(self, parent, title="Parámetros del Reporte"):
        super().__init__(parent, text=title, padding=10)
        self.controls = {}  # Diccionario de controles
        self._create_date_widgets()
    
    def _create_date_widgets(self):
        """Crea controles de fecha comunes"""
        # Fecha desde
        ttk.Label(self, text="Desde:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.date_from = ttk.Entry(self, width=12)
        self.date_from.grid(row=0, column=1, padx=5, pady=5)
        self.date_from.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        # Fecha hasta
        ttk.Label(self, text="Hasta:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.date_to = ttk.Entry(self, width=12)
        self.date_to.grid(row=0, column=3, padx=5, pady=5)
        self.date_to.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        self.controls['date_from'] = self.date_from
        self.controls['date_to'] = self.date_to
    
    def add_department_filter(self, departments):
        """Agrega filtro por departamento"""
        row = len(self.grid_slaves()) // 4
        
        ttk.Label(self, text="Departamento:").grid(
            row=row, column=0, sticky='w', padx=5, pady=5
        )
        
        self.dept_combo = ttk.Combobox(
            self, 
            values=["Todos"] + departments,
            state="readonly",
            width=20
        )
        self.dept_combo.grid(row=row, column=1, columnspan=3, sticky='ew', padx=5, pady=5)
        self.dept_combo.set("Todos")
        
        self.controls['department'] = self.dept_combo
    
    def add_status_filter(self):
        """Agrega filtro por estado"""
        row = len(self.grid_slaves()) // 4
        
        ttk.Label(self, text="Estado:").grid(
            row=row, column=0, sticky='w', padx=5, pady=5
        )
        
        self.status_combo = ttk.Combobox(
            self, 
            values=["Todos", "Pendiente", "Liquidado", "Vencido"],
            state="readonly",
            width=15
        )
        self.status_combo.grid(row=row, column=1, sticky='w', padx=5, pady=5)
        self.status_combo.set("Todos")
        
        self.controls['status'] = self.status_combo
    
    def get_params(self):
        """Obtiene todos los parámetros como diccionario"""
        params = {}
        for key, control in self.controls.items():
            if isinstance(control, ttk.Entry):
                params[key] = control.get()
            elif isinstance(control, ttk.Combobox):
                params[key] = control.get()
        return params