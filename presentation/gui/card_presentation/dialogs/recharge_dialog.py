import tkinter as tk
from tkinter import ttk, messagebox

class RechargeDialog:
    """Diálogo para recargar tarjetas"""
    
    def __init__(self, parent, card):
        self.parent = parent
        self.card = card
        self.result = None
        self.amount = None
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Crea el diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Recargar Tarjeta")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar el diálogo
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información de la tarjeta
        info_frame = ttk.LabelFrame(main_frame, text="Información de la Tarjeta", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        card_number = getattr(self.card, 'card_number', 'N/A')
        displayed_number = f"**** **** **** {card_number[-4:]}" if len(card_number) >= 4 else card_number
        ttk.Label(info_frame, text=f"Número: {displayed_number}").pack(anchor=tk.W, pady=2)
        
        balance = getattr(self.card, 'balance', 0)
        ttk.Label(info_frame, text=f"Balance actual: ${balance:.2f}").pack(anchor=tk.W, pady=2)
        
        # Campo para el monto
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(amount_frame, text="Monto a recargar:").pack(side=tk.LEFT)
        
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=20)
        self.amount_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.amount_entry.focus_set()
        
        ttk.Label(amount_frame, text="USD").pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Recargar", command=self._confirm_recharge).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def _confirm_recharge(self):
        """Confirma la recarga"""
        amount_str = self.amount_var.get().strip()
        
        if not amount_str:
            messagebox.showerror("Error", "Ingresa un monto", parent=self.dialog)
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Error", "El monto debe ser positivo", parent=self.dialog)
                return
                
            self.result = amount
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido", parent=self.dialog)
            return
    
    def show(self):
        """Muestra el diálogo y retorna el monto a recargar"""
        self.parent.wait_window(self.dialog)
        return self.result