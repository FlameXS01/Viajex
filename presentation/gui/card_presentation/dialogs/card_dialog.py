import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.card_presentation.widgets.card_form import CardForm
from application.services.card_service import CardService

class CardDialog:
    """Diálogo para crear/editar tarjetas"""
    
    def __init__(self, parent, card_service: CardService, card=None):
        self.parent = parent
        self.card_service = card_service
        self.card = card
        self.result = None
        
        self._create_dialog()

    def _create_dialog(self):
        """Crea el diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Editar Tarjeta" if self.card else "Crear Tarjeta")
        self.dialog.geometry("450x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Formulario
        self.form = CardForm(main_frame, self.card_service, self.card)
        self.form.pack(fill=tk.BOTH, expand=True)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20,0))
        
        ttk.Button(button_frame, text="Guardar", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _save(self):
        """Guarda la tarjeta - VERSIÓN CORREGIDA PARA MÚLTIPLES FIRMAS"""
        data = self.form.get_data()
        if data is None:
            return
            
        try:
            if self.card:
                # Diferentes formas de llamar a update_card basadas en la firma esperada
                try:
                    # Intento 1: Con argumentos posicionales
                    success = self.card_service.update_card(
                        self.card.id,
                        data['card_card_number'],
                        data['description'],
                        data['balance'],
                        data['is_active']
                    )
                except TypeError:
                    try:
                        # Intento 2: Con diccionario de datos
                        success = self.card_service.update_card({
                            'id': self.card.id,
                            'card_number': data['card_number'],
                            'description': data['description'],
                            'balance': data['balance'],
                            'is_active': data['is_active']
                        })
                    except TypeError:
                        # Intento 3: Con argumentos nombrados pero en orden diferente
                        success = self.card_service.update_card(
                            card_id=self.card.id,
                            card_card_number=data['card_number'],
                            description=data['description'],
                            balance=data['balance'],
                            is_active=data['is_active']
                        )
                
                if success:
                    messagebox.showinfo("Éxito", "Tarjeta actualizada correctamente")
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la tarjeta")
                    
            else:
                # Diferentes formas de llamar a create_card basadas en la firma esperada
                try:
                    # Intento 1: Con argumentos posicionales
                    success = self.card_service.create_card(
                        data['card_number'],
                        data['card_pin'],
                        data['balance'],
                    )
                except TypeError:
                    try:
                        # Intento 2: Con diccionario de datos
                        success = self.card_service.create_card({
                            'card_number': data['card_number'],
                            'description': data['description'],
                            'card_pin': data['card_pin'],
                            'balance': data['balance'],
                            'is_active': data['is_active']
                        })
                    except TypeError:
                        try:
                            # Intento 3: Con argumentos en orden diferente
                            success = self.card_service.create_card(
                                data['card_card_number'],
                                data['card_pin'],
                                data['balance'],
                                data['description'],
                                data['is_active']
                            )
                        except TypeError:
                            # Intento 4: Con menos parámetros
                            success = self.card_service.create_card(
                                card_card_number = data['card_card_number'],
                                card_pin = data['card_pin'],
                                amount = data['balance']
                            )
                
                if success:
                    messagebox.showinfo("Éxito", "Tarjeta creada correctamente")
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear la tarjeta")
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la tarjeta: {str(e)}")
            traceback.print(e)
            # Para debugging - mostrar información completa del error
            import traceback
            print("Error completo:", traceback.format_exc())

    def show(self):
        """Muestra el diálogo y retorna el resultado"""
        self.parent.wait_window(self.dialog)
        return self.result