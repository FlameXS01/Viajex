import tkinter as tk
from tkinter import ttk

class CardList(ttk.Frame):
    """Componente de lista de tarjetas optimizado"""
    
    def __init__(self, parent, on_select_callback=None):
        super().__init__(parent)
        self.on_select_callback = on_select_callback
        self.selected_card_id = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea la lista con scrollbars"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ('card_number', 'pin', 'balance', 'status')
        self.tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show='headings',
            height=10
        )
        
        # Configurar columnas
        self.tree.heading('card_number', text='Número de Tarjeta')
        self.tree.heading('pin', text='PIN')
        self.tree.heading('balance', text='Balance')
        self.tree.heading('status', text='Estado')
        
        self.tree.column('card_number', width=200)
        self.tree.column('pin', width=80, anchor='center')
        self.tree.column('balance', width=100, anchor='center')
        self.tree.column('status', width=80, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Binding para selección
        if self.on_select_callback:
            self.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def _on_select(self, event):
        """Maneja selección en la lista"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_card_id = item['tags'][0] if item['tags'] else None
        else:
            self.selected_card_id = None
        
        if self.on_select_callback:
            self.on_select_callback(self.selected_card_id)
    
    def load_cards(self, cards):
        """Carga tarjetas en la lista"""
        self.tree.delete(*self.tree.get_children())
        
        for card in cards:
            card_number = getattr(card, 'card_number', 'N/A')
            pin = getattr(card, 'card_pin', '0000')
            balance = getattr(card, 'balance', 0)
            is_active = getattr(card, 'is_active', True)
            status = "Activa" if is_active else "Inactiva"
            
            # Formatear número de tarjeta para mostrar
            display_number = card_number
            if len(card_number) >= 4:
                display_number = f"**** **** **** {card_number[-4:]}"
            
            self.tree.insert("", "end", 
                           values=(display_number, pin, f"${balance:.2f}", status),
                           tags=(card.id,))