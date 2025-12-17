from tkinter import ttk
import tkinter as tk

class TransactionDetailsDialog:
    """Diálogo para mostrar detalles completos de una transacción"""
    
    def __init__(self, parent, transaction):
        self.parent = parent
        self.transaction = transaction
        
        self._create_dialog()
    
    def _create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Detalles de Transacción #{self.transaction.id}")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
       