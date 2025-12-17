import tkinter as tk
from tkinter import ttk, messagebox

class TransactionSummaryPanel(ttk.LabelFrame):
    """Panel de resumen estadístico en tiempo real"""
    
    def __init__(self, parent):
        super().__init__(parent, text="Resumen del Período", padding="15")
        
        self._create_summary_metrics()
    
    def _create_summary_metrics(self):
        """Crea métricas principales"""
        metrics_frame = ttk.Frame(self)
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Métricas (usando Grid para alineación)
        ttk.Label(metrics_frame, text="Total Créditos:", font=('Arial', 10)).grid(row=0, column=0, sticky='w')
        self.total_credits_label = ttk.Label(metrics_frame, text="$0.00", font=('Arial', 10, 'bold'), foreground='green')
        self.total_credits_label.grid(row=0, column=1, padx=(10, 30))
        
        ttk.Label(metrics_frame, text="Total Débitos:", font=('Arial', 10)).grid(row=0, column=2, sticky='w')
        self.total_debits_label = ttk.Label(metrics_frame, text="$0.00", font=('Arial', 10, 'bold'), foreground='red')
        self.total_debits_label.grid(row=0, column=3, padx=(10, 30))
        
    