import tkinter as tk
from tkinter import ttk

class CardList(ttk.Frame):
    """Componente de lista de tarjetas - VERSIÓN ACTUALIZADA CON MONTO"""
    
    def __init__(self, parent, on_select_callback):
        super().__init__(parent)
        self.on_select_callback = on_select_callback
        self.selected_card_id = None
        
        self._create_widgets()
        self._setup_styles()

    def _setup_styles(self):
        """Configura estilos para el treeview"""
        style = ttk.Style()
        style.configure('Card.Treeview', rowheight=25)
        style.configure('Card.Treeview.Heading', font=('Arial', 10, 'bold'))

    def _create_widgets(self):
        """Crea los widgets de la lista"""
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar las tarjetas
        columns = ('id', 'number', 'balance', 'status', 'created_at')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', style='Card.Treeview')
        
        # Configurar columnas
        self.tree.heading('id', text='ID')
        self.tree.heading('number', text='Número')
        self.tree.heading('balance', text='Monto')
        self.tree.heading('status', text='Estado')
        self.tree.heading('created_at', text='Creado')
        
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('number', width=150)
        self.tree.column('balance', width=100, anchor='center')
        self.tree.column('status', width=100, anchor='center')
        self.tree.column('created_at', width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

    def _on_tree_select(self, event):
        """Maneja la selección en el treeview"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.selected_card_id = item['values'][0]
        else:
            self.selected_card_id = None
        
        self.on_select_callback(self.selected_card_id)

    def load_cards(self, cards):
        """Carga la lista de tarjetas"""
        self.tree.delete(*self.tree.get_children())
        
        for card in cards:
            # Formatear fecha si está disponible
            created_at = getattr(card, 'created_at', 'N/A')
            if hasattr(created_at, 'strftime'):
                created_at = created_at.strftime('%Y-%m-%d')
            
            # Formatear monto
            balance = getattr(card, 'balance', 0)
            balance_str = f"${balance:.2f}" if isinstance(balance, (int, float)) else str(balance)
            
            # Insertar en el treeview
            item_id = self.tree.insert('', tk.END, values=(
                card.id, 
                card.name, 
                balance_str,
                '✅ Activa' if card.is_active else '❌ Inactiva',
                created_at
            ))