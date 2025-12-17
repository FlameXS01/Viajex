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
        
        # Contenido con secciones claras
        self._create_info_section()
        self._create_balance_section()
        self._create_metadata_section()