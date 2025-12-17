import tkinter as tk
from tkinter import ttk, messagebox
from application.services.card_service import CardService

class CardDialog:
    """Diálogo simplificado para crear/editar tarjetas"""
    
    def __init__(self, parent, card_service: CardService, card=None):
        self.parent = parent
        self.card_service = card_service
        self.card = card
        self.edit_mode = bool(card)
        
        self._create_dialog()
        self._create_form()
    
    def _create_dialog(self):
        """Crea la ventana de diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Editar Tarjeta" if self.edit_mode else "Crear Tarjeta")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Centrar diálogo
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 150
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_form(self):
        """Crea el formulario"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Número de tarjeta
        ttk.Label(main_frame, text="Número de Tarjeta:").grid(
            row=0, column=0, sticky='w', pady=(0, 5)
        )
        self.card_number_var = tk.StringVar()
        self.card_number_entry = ttk.Entry(
            main_frame, 
            textvariable=self.card_number_var,
            width=25
        )
        self.card_number_entry.grid(row=0, column=1, sticky='w', pady=(0, 5), padx=(10, 0))
        
        # PIN
        ttk.Label(main_frame, text="PIN (4 dígitos):").grid(
            row=1, column=0, sticky='w', pady=(0, 5)
        )
        self.pin_var = tk.StringVar()
        self.pin_entry = ttk.Entry(
            main_frame,
            textvariable=self.pin_var,
            width=25,
            show="*"
        )
        self.pin_entry.grid(row=1, column=1, sticky='w', pady=(0, 5), padx=(10, 0))
        
        # Balance (solo para creación)
        if not self.edit_mode:
            ttk.Label(main_frame, text="Balance Inicial:").grid(
                row=2, column=0, sticky='w', pady=(0, 5)
            )
            self.balance_var = tk.StringVar()
            self.balance_entry = ttk.Entry(
                main_frame,
                textvariable=self.balance_var,
                width=25
            )
            self.balance_entry.grid(row=2, column=1, sticky='w', pady=(0, 5), padx=(10, 0))
        
        # Estado
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Tarjeta Activa",
            variable=self.active_var
        ).grid(row=3, column=0, columnspan=2, sticky='w', pady=(10, 0))
        
        # Cargar datos si es edición
        if self.edit_mode and self.card:
            self.card_number_var.set(getattr(self.card, 'card_number', ''))
            self.pin_var.set(getattr(self.card, 'card_pin', ''))
            self.active_var.set(getattr(self.card, 'is_active', True))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="Guardar",
            command=self._save
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
        
        # Enfocar primer campo
        if self.edit_mode:
            self.card_number_entry.focus()
        else:
            self.card_number_entry.focus()
    
    def _save(self):
        """Guarda los datos de la tarjeta"""
        # Validar datos
        card_number = self.card_number_var.get().strip()
        pin = self.pin_var.get().strip()
        
        if not card_number:
            messagebox.showerror("Error", "El número de tarjeta es requerido")
            return
        
        if not pin or len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Error", "El PIN debe tener 4 dígitos")
            return
        
        try:
            if self.edit_mode and self.card:
                # Actualizar tarjeta existente
                updated = self.card_service.update_card(
                    card_id=self.card.id,
                    card_number=card_number,
                    card_pin=pin
                )
                if updated:
                    messagebox.showinfo("Éxito", "Tarjeta actualizada")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar")
            else:
                # Crear nueva tarjeta
                balance_str = self.balance_var.get().strip() if hasattr(self, 'balance_var') else "0"
                
                try:
                    balance = float(balance_str) if balance_str else 0
                    if balance < 0:
                        messagebox.showerror("Error", "El balance no puede ser negativo")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Balance inválido")
                    return
                
                new_card = self.card_service.create_card(
                    card_number=card_number,
                    card_pin=pin,
                    amount=balance
                )
                
                if new_card:
                    messagebox.showinfo("Éxito", "Tarjeta creada")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear tarjeta")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def show(self):
        """Muestra el diálogo"""
        self.parent.wait_window(self.dialog)
        return True