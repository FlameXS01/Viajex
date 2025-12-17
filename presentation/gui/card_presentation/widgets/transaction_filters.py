import tkinter as tk
from tkinter import ttk

class TransactionFilters(ttk.Frame):
    """Componente de filtros para transacciones"""
    
    def __init__(self, parent, on_filter_change):
        super().__init__(parent)
        self.on_filter_change = on_filter_change
        
        self._create_date_filters()
        self._create_type_filters()
        self._create_amount_filters()