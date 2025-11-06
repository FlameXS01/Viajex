import tkinter as tk
from tkinter import ttk, messagebox

class CardForm(ttk.Frame):
    """Formulario para crear/editar tarjetas - VERSIÓN ACTUALIZADA CON PIN Y MONTO"""
    
    def __init__(self, parent, card_service, card=None):
        super().__init__(parent)
        self.card_service = card_service
        self.card = card
        
        self._create_widgets()
        if self.card:
            self._load_data()

    def _create_widgets(self):
        """Crea los campos del formulario"""
        # Número
        ttk.Label(self, text="Número:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.number_entry = ttk.Entry(self, width=30)
        self.number_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5,0))
        
        # Descripción
        ttk.Label(self, text="Descripción:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(self, width=30, height=4)
        self.desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5,0))
        
        # PIN de la tarjeta
        ttk.Label(self, text="PIN:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.pin_entry = ttk.Entry(self, width=30, show="*")
        self.pin_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5,0))
        
        # Monto (balance)
        ttk.Label(self, text="Monto:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.balance_entry = ttk.Entry(self, width=30)
        self.balance_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5,0))
        
        # Estado (activo/inactivo)
        self.status_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Activa", variable=self.status_var).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        self.grid_columnconfigure(1, weight=1)

    def _load_data(self):
        """Carga los datos de la tarjeta en el formulario (para edición)"""
        self.number_entry.insert(0, self.card.name)
        self.desc_text.insert('1.0', self.card.description)
        # Nota: Por seguridad, no cargamos el PIN en la edición
        # self.pin_entry.insert(0, self.card.card_pin)  # No hacemos esto
        self.balance_entry.insert(0, str(self.card.balance))
        self.status_var.set(self.card.is_active)

    def get_data(self):
        """Obtiene los datos del formulario"""
        card_name = self.number_entry.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        pin = self.pin_entry.get().strip()
        balance_str = self.balance_entry.get().strip()
        is_active = self.status_var.get()
        
        # Validaciones
        if not card_name:
            messagebox.showerror("Error", "El número es obligatorio")
            return None
            
        if not pin:
            messagebox.showerror("Error", "El PIN es obligatorio")
            return None
            
        if not balance_str:
            messagebox.showerror("Error", "El monto es obligatorio")
            return None
            
        try:
            balance = float(balance_str)
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
            return None
            
        return {
            'card_name': card_name,
            'description': description,
            'card_pin': pin,
            'balance': balance,
            'is_active': is_active
        }