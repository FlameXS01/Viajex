import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ReportActions(ttk.Frame):
    """Panel de acciones para reportes (exportar, imprimir, generar)"""
    
    def __init__(self, parent, callbacks):
        super().__init__(parent)
        self.callbacks = callbacks  # Dict con funciones callback
        self._create_widgets()
    
    def _create_widgets(self):
        # Botón de generar reporte
        self.generate_btn = ttk.Button(
            self, 
            text="Generar Reporte", 
            command=self.callbacks.get('generate', None),
            state=tk.NORMAL
        )
        self.generate_btn.pack(side='left', padx=5)
        
        # Botón de exportar a CSV
        self.csv_btn = ttk.Button(
            self, 
            text="Exportar CSV", 
            command=self.callbacks.get('export_csv', None),
            state=tk.NORMAL
        )
        self.csv_btn.pack(side='left', padx=5)
        
        # Botón de exportar a Excel
        self.excel_btn = ttk.Button(
            self, 
            text="Exportar Excel", 
            command=self.callbacks.get('export_excel', None),
            state=tk.NORMAL
        )
        self.excel_btn.pack(side='left', padx=5)
        
        # Botón de imprimir (si es necesario)
        self.print_btn = ttk.Button(
            self, 
            text="Vista Impresión", 
            command=self.callbacks.get('print', None),
            state=tk.NORMAL
        )
        self.print_btn.pack(side='left', padx=5)
    
    def set_buttons_state(self, state):
        """Habilita/deshabilita todos los botones"""
        self.generate_btn.config(state=state)
        self.csv_btn.config(state=state)
        self.excel_btn.config(state=state)
        self.print_btn.config(state=state)