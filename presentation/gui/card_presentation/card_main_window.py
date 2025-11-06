import tkinter as tk
from tkinter import messagebox, ttk
from application.services.card_service import CardService

# Importar componentes modulares
from presentation.gui.utils.windows_utils import WindowUtils
from presentation.gui.card_presentation.widgets.card_list import CardList
from presentation.gui.card_presentation.widgets.card_actions import CardActions
from presentation.gui.card_presentation.dialogs.card_dialog import CardDialog
from presentation.gui.card_presentation.dialogs.confirm_dialog import ConfirmDialog

class CardMainWindow:
    """Ventana principal para la gestión de tarjetas"""
    
    def __init__(self, parent, card_service: CardService):
        self.parent = parent
        self.card_service = card_service
        self.selected_card_id = None
        
        self._create_widgets()
        self._load_cards()

    def _create_widgets(self):
        """Crea los widgets principales usando componentes modulares"""
        main_frame = ttk.Frame(self.parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Gestión de Tarjetas", 
                                font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Botón para crear tarjeta
        create_button = ttk.Button(main_frame, text="Crear Nueva Tarjeta", 
                                command=self._create_card)
        create_button.grid(row=1, column=0, sticky=tk.W, pady=(0, 15))
        
        # Lista de tarjetas (componente modular)
        list_frame = ttk.LabelFrame(main_frame, text="Tarjetas Existentes", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.card_list = CardList(list_frame, self._on_card_select)
        self.card_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Acciones de tarjeta (componente modular)
        actions_frame = ttk.LabelFrame(main_frame, text="Acciones", padding="15")
        actions_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.card_actions = CardActions(actions_frame, {
            'edit': self._edit_card,
            'toggle_active': self._toggle_active,
            'delete': self._delete_card
        })
        self.card_actions.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def _on_card_select(self, card_id):
        """Maneja la selección de tarjetas"""
        self.selected_card_id = card_id
        if card_id:
            self.card_actions.set_buttons_state(tk.NORMAL)
        else:
            self.card_actions.set_buttons_state(tk.DISABLED)

    def _create_card(self):
        """Abre diálogo para crear nueva tarjeta"""
        dialog = CardDialog(self.parent, self.card_service)
        result = dialog.show()
        if result:
            self._load_cards()

    def _edit_card(self):
        """Abre diálogo para editar tarjeta existente"""
        if not self.selected_card_id:
            return
            
        card = self.card_service.get_card_by_id(self.selected_card_id)
        if card:
            dialog = CardDialog(self.parent, self.card_service, card)
            result = dialog.show()
            if result:
                self._load_cards()

    def _toggle_active(self):
        """Activa/desactiva la tarjeta seleccionada"""
        if not self.selected_card_id:
            return
            
        try:
            card = self.card_service.toggle_card_active(self.selected_card_id)
            status = "activada" if card.is_active else "desactivada"
            messagebox.showinfo("Éxito", f"Tarjeta {status} correctamente")
            self._load_cards()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el estado: {str(e)}")

    def _delete_card(self):
        """Elimina la tarjeta seleccionada"""
        if not self.selected_card_id:
            return
            
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

        ConfirmDialog(
            self.parent,
            "Confirmar Eliminación",
            f"¿Estás seguro de que quieres eliminar la tarjeta '{card.name}'?\nEsta acción no se puede deshacer.",
            confirm_delete
        )

    def _load_cards(self):
        """Carga las tarjetas en la lista"""
        try:
            cards = self.card_service.get_all_cards()
            self.card_list.load_cards(cards)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las tarjetas: {str(e)}")