import tkinter as tk
from tkinter import ttk, messagebox

class RechargeDialog:
    """Diálogo simplificado para recargar tarjetas"""
    
    def __init__(self, parent, card):
        self.parent = parent
        self.card = card
        self.amount = None
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Crea el diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Recargar Tarjeta")
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        
        # Centrar
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 175
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 125
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_content()
    
    def _create_content(self):
        """Crea el contenido del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información de tarjeta
        card_info = ttk.LabelFrame(main_frame, text="Información", padding="10")
        card_info.pack(fill=tk.X, pady=(0, 15))
        
        card_number = getattr(self.card, 'card_number', 'N/A')
        if len(card_number) >= 4:
            display_num = f"**** **** **** {card_number[-4:]}"
        else:
            display_num = card_number
        
        ttk.Label(card_info, text=f"Número: {display_num}").pack(anchor='w')
        
        balance = getattr(self.card, 'balance', 0)
        ttk.Label(card_info, text=f"Saldo actual: ${balance:.2f}").pack(anchor='w')
        
        # Campo de monto
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(amount_frame, text="Monto a recargar:").pack(side=tk.LEFT)
        
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(
            amount_frame,
            textvariable=self.amount_var,
            width=15
        )
        self.amount_entry.pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(amount_frame, text="CUP").pack(side=tk.LEFT)
        
        # Botones predefinidos
        quick_frame = ttk.Frame(main_frame)
        quick_frame.pack(fill=tk.X, pady=(0, 15))
        
        amounts = [10, 20, 50, 100, 200]
        for amount in amounts:
            btn = ttk.Button(
                quick_frame,
                text=f"${amount}",
                width=6,
                command=lambda a=amount: self.amount_var.set(str(a))
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Recargar",
            command=self._confirm
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Enfocar campo de monto
        self.amount_entry.focus()
    
    def _confirm(self):
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
            
            self.amount = amount
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Monto inválido", parent=self.dialog)
    
    def show(self):
        """Muestra el diálogo y retorna el monto"""
        self.parent.wait_window(self.dialog)
        return self.amount