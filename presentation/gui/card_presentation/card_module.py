import tkinter as tk
from tkinter import ttk, messagebox
from application.services.card_service import CardService

# Importar componentes modulares de cards
from presentation.gui.card_presentation.widgets.card_list import CardList
from presentation.gui.card_presentation.widgets.card_actions import CardActions
from presentation.gui.card_presentation.dialogs.card_dialog import CardDialog
from presentation.gui.card_presentation.dialogs.confirm_dialog import ConfirmDialog

class CardModule(ttk.Frame):
    """Módulo de gestión de tarjetas para embeber en el dashboard"""
    
    def __init__(self, parent, card_service: CardService):
        super().__init__(parent, style='Content.TFrame')
        self.card_service = card_service
        self.selected_card_id = None
        
        self._create_widgets()
        self._load_cards()

    def _create_widgets(self):
        """Crea la interfaz del módulo de tarjetas"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header del módulo
        header_frame = ttk.Frame(self, style='Content.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(header_frame, text="Gestión de Tarjetas", 
                    font=('Arial', 18, 'bold'), style='Content.TLabel').grid(row=0, column=0, sticky='w')
        
        # Botón de crear tarjeta
        create_btn = ttk.Button(header_frame, text="➕ Crear Tarjeta", 
                                command=self._create_card)
        create_btn.grid(row=0, column=1, sticky='e', padx=(0, 10))
        
        # Contenido principal (lista + acciones)
        content_frame = ttk.Frame(self, style='Content.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew')
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Lista de tarjetas
        list_frame = ttk.LabelFrame(content_frame, text="Tarjetas Registradas", padding="15")
        list_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.card_list = CardList(list_frame, self._on_card_select)
        self.card_list.grid(row=0, column=0, sticky='nsew')
        
        # Panel de acciones
        actions_frame = ttk.LabelFrame(content_frame, text="Acciones Disponibles", padding="15")
        actions_frame.grid(row=1, column=0, sticky='ew')
        
        self.card_actions = CardActions(actions_frame, {
            'edit': self._edit_card,
            'toggle_active': self._toggle_active,
            'delete': self._delete_card
        })
        self.card_actions.grid(row=0, column=0, sticky='ew')

    def _on_card_select(self, event):
        """Maneja la selección de tarjetas en la lista - obtener ID desde tags"""
        selection = self.card_list.tree.selection()
        if selection:
            # CAMBIAR: Obtener el ID desde los tags en lugar de desde la columna
            item = self.card_list.tree.item(selection[0])
            card_id = item['tags'][0] if item['tags'] else None  
            self.selected_card_id = card_id
            self.card_actions.set_buttons_state(tk.NORMAL)
        else:
            self.selected_card_id = None
            self.card_actions.set_buttons_state(tk.DISABLED)

    def _create_card(self):
        """Abre diálogo para crear nueva tarjeta"""
        try:
            dialog = CardDialog(self.winfo_toplevel(), self.card_service)
            result = dialog.show()
            if result:
                self._load_cards()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el diálogo: {str(e)}")

    def _edit_card(self):
        """Abre diálogo para editar tarjeta existente"""
        if not self.selected_card_id:
            return
            
        try:
            card = self.card_service.get_card_by_id(self.selected_card_id)
            if card:
                dialog = CardDialog(self.winfo_toplevel(), self.card_service, card)
                result = dialog.show()
                if result:
                    self._load_cards()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar la tarjeta: {str(e)}")

    def _toggle_active(self):
        """Activa/desactiva la tarjeta seleccionada"""
        if not self.selected_card_id:
            return
            
        try:
            card = self.card_service.toggle_card_active(self.selected_card_id)
            if not card:
                return messagebox.showerror("Error", "Tarjeta no encontrada")
            status = "activada" if card.is_active else "desactivada"
            messagebox.showinfo("Éxito", f"Tarjeta {status} correctamente")
            self._load_cards()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el estado: {str(e)}")

    def _delete_card(self):
        """Elimina la tarjeta seleccionada - SIN DESCRIPTION"""
        if not self.selected_card_id:
            return
            
        try:
            card = self.card_service.get_card_by_id(self.selected_card_id)
            if not card:
                messagebox.showerror("Error", "Tarjeta no encontrada")
                return
                
            def confirm_delete():
                try:
                    success = self.card_service.delete_card(self.selected_card_id)
                    if success:
                        messagebox.showinfo("Éxito", "Tarjeta eliminada correctamente")
                        self.selected_card_id = None
                        self._load_cards()
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar la tarjeta")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar la tarjeta: {str(e)}")

            # Mostrar información de la tarjeta (SIN DESCRIPTION)
            card_number = getattr(card, 'card_number', 'N/A')
            card_info = f"Número: **** **** **** {card_number[-4:]}\n" if len(card_number) >= 4 else f"Número: {card_number}\n"
            card_info += f"Balance: ${card.balance:.2f}\n" if hasattr(card, 'balance') else ""

            ConfirmDialog(
                self.winfo_toplevel(),
                "Confirmar Eliminación",
                f"¿Estás seguro de que quieres eliminar la siguiente tarjeta?\n\n{card_info}\nEsta acción no se puede deshacer.",
                confirm_delete,
                confirm_text="Eliminar",
                cancel_text="Cancelar"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar tarjeta: {str(e)}")

    def _load_cards(self):
        """Carga las tarjetas en la lista"""
        try:
            cards = self.card_service.get_all_cards()
            self.card_list.load_cards(cards)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las tarjetas: {str(e)}")