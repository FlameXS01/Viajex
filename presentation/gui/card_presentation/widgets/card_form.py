import tkinter as tk
from tkinter import ttk, messagebox

class CardForm(ttk.Frame):
    """Formulario para crear/editar tarjetas - SIN DESCRIPTION"""
    
    def __init__(self, parent, card_service, card=None):
        super().__init__(parent)
        self.card_service = card_service
        self.card = card
        
        self._create_widgets()
        if self.card:
            self._load_data()

    def _create_widgets(self):
        """Crea los campos del formulario"""
        ttk.Label(self, text="Número de Tarjeta (12-16 dígitos):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.card_number_entry = ttk.Entry(self, width=30)
        self.card_number_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5,0))
        
        ttk.Label(self, text="PIN:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pin_entry = ttk.Entry(self, width=30)
        self.pin_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5,0))
        
        
        ttk.Label(self, text="Balance:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.balance_entry = ttk.Entry(self, width=30)
        self.balance_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5,0))
        
    
        self.status_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Activa", variable=self.status_var).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        self.grid_columnconfigure(1, weight=1)

    def _load_data(self):
        """Carga los datos de la tarjeta en el formulario (para edición)"""
        self.card_number_entry.insert(0, getattr(self.card, 'card_number', ''))
        self.pin_entry.insert(0, getattr(self.card, 'card_pin', ''))
        self.balance_entry.insert(0, str(getattr(self.card, 'balance', 0)))
        self.status_var.set(getattr(self.card, 'is_active', True))

    def get_data(self):
        """Obtiene los datos del formulario"""
        card_number = self.card_number_entry.get().strip()
        pin = self.pin_entry.get().strip()
        balance_str = self.balance_entry.get().strip()
        is_active = self.status_var.get()
        
        # Validaciones
        if not card_number:
            messagebox.showerror("Error", "El número de tarjeta es obligatorio")
            return None
        
        if len(card_number) < 12 or len(card_number) > 16 or not card_number.isdigit():
            messagebox.showerror("Error", "El número de tarjeta debe tener entre 12 y 16 dígitos")
            return None
            
        if not pin:
            messagebox.showerror("Error", "El PIN es obligatorio")
            return None
            
        if len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Error", "El PIN debe tener exactamente 4 dígitos")
            return None
            
        if not balance_str:
            messagebox.showerror("Error", "El balance es obligatorio")
            return None
            
        try:
            balance = float(balance_str)
            if balance < 0:
                messagebox.showerror("Error", "El balance no puede ser negativo")
                return None
        except ValueError:
            messagebox.showerror("Error", "El balance debe ser un número válido")
            return None
            
        return {
            'card_number': card_number,
            'card_pin': pin,
            'balance': balance,
            'is_active': is_active
        }