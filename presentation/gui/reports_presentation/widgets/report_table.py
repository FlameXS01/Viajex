import tkinter as tk
from tkinter import ttk
from datetime import datetime

class ReportTable(ttk.Frame):
    """Widget de tabla para visualizar reportes con scrollbars y formato condicional"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.tree = None
        self._create_widgets()
    
    def _create_widgets(self):
        # Frame principal con scrollbars
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill='both', expand=True)
        
        # Treeview con scrollbars
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    def set_columns(self, columns, widths=None):
        """Configura las columnas de la tabla"""
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            width = widths[i] if widths and i < len(widths) else 100
            self.tree.column(col, width=width, stretch=True)
    
    def load_data(self, data, apply_colors=False):
        """Carga datos en la tabla"""
        # Limpiar tabla existente
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insertar nuevos datos
        for row in data:
            item_id = self.tree.insert("", "end", values=row)
            
            # Aplicar colores condicionales (ej: vencidos en rojo)
            if apply_colors:
                self._apply_conditional_formatting(item_id, row)
    
    def _apply_conditional_formatting(self, item_id, row):
        """Aplica formato condicional basado en datos"""
        # Ejemplo: Si la columna 4 contiene días transcurridos > 5, poner rojo
        if len(row) > 4 and str(row[4]).isdigit():
            if int(row[4]) > 5:
                self.tree.item(item_id, tags=('overdue',))
                self.tree.tag_configure('overdue', background='#ffcccc')