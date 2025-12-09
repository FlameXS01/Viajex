import tkinter as tk
from tkinter import ttk, messagebox
from application.services.card_service import CardService
from presentation.gui.card_presentation.widgets.card_form import CardForm

class CardDialog:
    """Diálogo para crear/editar tarjetas"""
    
    def __init__(self, parent, card_service: CardService, card=None):
        self.parent = parent
        self.card_service = card_service
        self.card = card
        self.result = None
        self.edit_mode = True if self.card else False
        
        self._create_dialog()

    def _create_dialog(self):
        """Crea el diálogo"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Editar Tarjeta" if self.edit_mode else "Crear Tarjeta")
        self.dialog.geometry("450x350")  
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
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
        self.form = CardForm(main_frame, self.card_service, self.edit_mode, self.card)
        self.form.pack(fill=tk.BOTH, expand=True)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20,0))
        
        ttk.Button(button_frame, text="Guardar", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _save(self):
        """Guarda la tarjeta - VERSIÓN CORREGIDA"""
        data = self.form.get_data()
        if data is None:
            return
            
        try:
            if self.card:
                updated_card = self.card_service.update_card(
                    card_id=self.card.id,
                    card_number=data['card_number'],
                    card_pin=data['card_pin'] 
                )
                success = updated_card is not None
            else:
                # Para crear
                new_card = self.card_service.create_card(
                    card_number=data['card_number'],
                    card_pin=data['card_pin'],
                    amount=data['balance']
                )
                success = new_card is not None
                
            if success:
                messagebox.showinfo("Éxito", "Tarjeta guardada correctamente")
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar la tarjeta")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la tarjeta: {str(e)}")
            import traceback
            print("Error completo:", traceback.format_exc())

    def show(self):
        """Muestra el diálogo y retorna el resultado"""
        self.parent.wait_window(self.dialog)
        return self.result