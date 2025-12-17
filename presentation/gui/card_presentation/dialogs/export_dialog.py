import tkinter as tk
from tkinter import ttk

class ExportDialog:
    """Diálogo para exportar historial de transacciones"""
    
    def __init__(self, parent, card_id, transaction_service):
        self.parent = parent
        self.card_id = card_id
        self.transaction_service = transaction_service
        
        self._create_dialog()
        self._create_export_options()
    
    def _create_export_options(self):
        """Crea opciones de exportación"""
        # Formato (CSV, Excel, JSON)
        self.format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(self.dialog, text="CSV", variable=self.format_var, value="csv").pack(anchor='w')
        ttk.Radiobutton(self.dialog, text="Excel", variable=self.format_var, value="excel").pack(anchor='w')
        ttk.Radiobutton(self.dialog, text="JSON", variable=self.format_var, value="json").pack(anchor='w')
        
        # Rango de fechas
        self.date_range_frame = ttk.LabelFrame(self.dialog, text="Rango de Fechas", padding="10")
        self.date_range_frame.pack(fill=tk.X, pady=10)
        
        # Opciones de inclusión
        self.include_summary_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.dialog, text="Incluir resumen", variable=self.include_summary_var).pack(anchor='w')