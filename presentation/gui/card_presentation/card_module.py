import tkinter as tk
from tkinter import ttk, messagebox
from application.services.card_service import CardService

# Importar componentes
from presentation.gui.card_presentation.widgets.card_list import CardList
from presentation.gui.card_presentation.widgets.card_actions import CardActions
from presentation.gui.card_presentation.widgets.transaction_history import TransactionHistoryPanel
from presentation.gui.card_presentation.dialogs.card_dialog import CardDialog
from presentation.gui.card_presentation.dialogs.recharge_dialog import RechargeDialog
from presentation.gui.card_presentation.dialogs.confirm_dialog import ConfirmDialog

class CardModule(ttk.Frame):
    """Módulo de gestión de tarjetas optimizado"""
    
    def __init__(self, parent, card_service: CardService, card_transaction_service=None):
        super().__init__(parent)
        self.card_service = card_service
        self.card_transaction_service = card_transaction_service
        self.selected_card_id = None
        self.selected_card = None
        
        self._create_widgets()
        self._load_cards()
    
    def _create_widgets(self):
        """Crea la interfaz del módulo"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew')
        
        # Pestaña 1: Gestión de Tarjetas
        self.cards_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cards_tab, text="Tarjetas")
        
        # Pestaña 2: Historial
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="Historial")
        
        # Inicialmente deshabilitar historial
        self.notebook.tab(1, state="disabled")
        
        # Crear contenido de pestañas
        self._create_cards_tab()
        self._create_history_tab()
        
        # Bind evento cambio de pestaña
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
    
    def _create_cards_tab(self):
        """Crea la pestaña de gestión de tarjetas"""
        # Configurar grid
        self.cards_tab.columnconfigure(0, weight=1)
        self.cards_tab.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.cards_tab)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(
            header_frame,
            text="Gestión de Tarjetas",
            font=('Arial', 16, 'bold')
        ).grid(row=0, column=0, sticky='w')
        
        # Botón crear
        ttk.Button(
            header_frame,
            text="Nueva Tarjeta",
            command=self._create_card
        ).grid(row=0, column=1, sticky='e', padx=5)
        
        # Lista de tarjetas
        list_frame = ttk.LabelFrame(self.cards_tab, text="Tarjetas", padding="10")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.card_list = CardList(list_frame, self._on_card_select)
        self.card_list.grid(row=0, column=0, sticky='nsew')
        
        # Panel de acciones
        actions_frame = ttk.LabelFrame(self.cards_tab, text="Acciones", padding="10")
        actions_frame.grid(row=2, column=0, sticky='ew')
        
        self.card_actions = CardActions(actions_frame, {
            'recharge': self._recharge_card,
            'edit': self._edit_card,
            'toggle_active': self._toggle_card_active,
            'delete': self._delete_card,
            'view_history': self._view_history
        })
        self.card_actions.grid(row=0, column=0, sticky='ew')
        
        # Deshabilitar acciones inicialmente
        self.card_actions.set_buttons_state(tk.DISABLED)
    
    def _create_history_tab(self):
        """Crea la pestaña de historial"""
        self.history_tab.columnconfigure(0, weight=1)
        self.history_tab.rowconfigure(1, weight=1)
        
        # Header del historial - SIN FRAME EXTRA
        self.history_title = ttk.Label(
            self.history_tab,
            text="📊 Historial de Transacciones",
            font=('Arial', 14, 'bold')
        )
        self.history_title.grid(row=0, column=0, sticky='w', pady=(5, 10))  # Reducido
        
        # Botón para volver a la lista - en la misma fila pero alineado a la derecha
        self.back_button = ttk.Button(
            self.history_tab,
            text="← Volver a Tarjetas",
            command=self._switch_to_cards_tab
        )
        self.back_button.grid(row=0, column=0, sticky='e', padx=5, pady=(5, 10))
        
        # Panel de historial de transacciones - con menos margen superior
        if self.card_transaction_service:
            self.transaction_history = TransactionHistoryPanel(
                self.history_tab,
                self.card_transaction_service
            )
            self.transaction_history.grid(row=1, column=0, sticky='nsew', pady=(0, 0))
        else:
            message_label = ttk.Label(
                self.history_tab,
                text="Servicio de transacciones no disponible",
                foreground='gray'
            )
            message_label.grid(row=1, column=0, sticky='nsew')
    
    def _load_cards(self):
        """Carga todas las tarjetas"""
        try:
            cards = self.card_service.get_all_cards()
            self.card_list.load_cards(cards)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar tarjetas: {str(e)}")
    
    def _on_card_select(self, card_id):
        """Maneja selección de tarjeta"""
        self.selected_card_id = card_id
        
        if card_id:
            try:
                self.selected_card = self.card_service.get_card_by_id(card_id)
                self.card_actions.set_buttons_state(tk.NORMAL)
                
                
                    
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar tarjeta: {str(e)}")
        else:
            self.selected_card = None
            self.card_actions.set_buttons_state(tk.DISABLED)
    
    def _create_card(self):
        """Crea nueva tarjeta"""
        try:
            dialog = CardDialog(self.winfo_toplevel(), self.card_service)
            result = dialog.show()
            if result:
                self._load_cards()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear tarjeta: {str(e)}")
    
    def _edit_card(self):
        """Edita tarjeta seleccionada"""
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
            messagebox.showerror("Error", f"No se pudo editar tarjeta: {str(e)}")
    
    def _recharge_card(self):
        """Recarga tarjeta seleccionada"""

        if not self.selected_card_id:
            messagebox.showwarning("Advertencia", "Selecciona una tarjeta")
            return
        
        try:
            card = self.card_service.get_card_by_id(self.selected_card_id)
            if not card:
                messagebox.showerror("Error", "Tarjeta no encontrada")
                return
            
            dialog = RechargeDialog(self.winfo_toplevel(), card)
            amount = dialog.show()
            
            if amount:
                success = self.card_service.recharge_card(self.selected_card_id, amount, is_refound = False)
                if success:
                    messagebox.showinfo("Éxito", f"Recarga exitosa: ${amount:.2f}")
                    self._load_cards()
                else:
                    messagebox.showerror("Error", "No se pudo realizar la recarga")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error en recarga: {str(e)}")
    
    def _toggle_card_active(self):
        """Activa/desactiva tarjeta"""
        if not self.selected_card_id:
            return
        
        try:
            card = self.card_service.toggle_card_active(self.selected_card_id)
            if card:
                status = "activada" if card.is_active else "desactivada"
                messagebox.showinfo("Éxito", f"Tarjeta {status}")
                self._load_cards()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar estado: {str(e)}")
    
    def _delete_card(self):
        """Elimina tarjeta seleccionada"""
        if not self.selected_card_id:
            return
        
        def confirm_delete():
            try:
                success = self.card_service.delete_card(self.selected_card_id)
                if success:
                    messagebox.showinfo("Éxito", "Tarjeta eliminada")
                    self.selected_card_id = None
                    self._load_cards()
                    self.card_actions.set_buttons_state(tk.DISABLED)
                else:
                    messagebox.showerror("Error", "No se pudo eliminar tarjeta")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
        
        # Mostrar diálogo de confirmación
        ConfirmDialog(
            self.winfo_toplevel(),
            "Confirmar Eliminación",
            "¿Estás seguro de eliminar esta tarjeta?\nEsta acción no se puede deshacer.",
            confirm_delete,
            confirm_text="Eliminar"
        )
    
    def _view_history(self):
        """Muestra historial de tarjeta"""
        if not self.selected_card_id:
            messagebox.showwarning("Advertencia", "Selecciona una tarjeta primero")
            return
        
        # Habilitar pestaña de historial
        self.notebook.tab(1, state="normal")
        self.notebook.select(1)
    
    def _switch_to_cards_tab(self):
        """Regresa a pestaña de tarjetas"""
        self.notebook.select(0)
    
    def _on_tab_changed(self, event):
        """Maneja cambio de pestaña"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 1:  
            if self.selected_card_id and hasattr(self, 'transaction_history'):
                self.transaction_history.load_card_history(
                    self.selected_card_id
                )
            else:
                self._switch_to_cards_tab()