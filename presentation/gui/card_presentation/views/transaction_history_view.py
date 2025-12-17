import tkinter as tk
from tkinter import ttk

from presentation.gui.card_presentation.widgets.transaction_filters import TransactionFilters
from presentation.gui.card_presentation.widgets.transaction_summary import TransactionSummaryPanel

class TransactionHistoryView(ttk.Frame):
    """Vista principal del historial de transacciones"""
    
    def __init__(self, parent, card_transaction_service):
        super().__init__(parent)
        self.card_transaction_service = card_transaction_service
        
        # Layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Filtros
        self.filters = TransactionFilters(self, self._on_filter_change)
        self.filters.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # 2. Resumen
        self.summary = TransactionSummaryPanel(self)
        self.summary.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        # 3. Lista de transacciones
        self.transaction_list = TransactionList(self, self._on_transaction_select)
        self.transaction_list.grid(row=2, column=0, sticky='nsew', pady=(0, 10))
        
        # 4. Acciones
        self._create_action_buttons()
    
    def _create_action_buttons(self):
        """Crea botones de acción"""
        action_frame = ttk.Frame(self)
        action_frame.grid(row=3, column=0, sticky='ew')
        
        ttk.Button(action_frame, text="🔄 Actualizar", command=self._refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📊 Gráfico", command=self._show_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📁 Exportar", command=self._export).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🖨️ Imprimir", command=self._print).pack(side=tk.LEFT, padx=5)