import tkinter as tk
from tkinter import ttk

class CardList(ttk.Frame):
    """Componente de lista de tarjetas - MEJORADO PARA DIFERENTES LONGITUDES"""
    
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
        columns = ('id', 'card_number', 'balance', 'status', 'created_at')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', style='Card.Treeview')
        
        # Configurar columnas
        self.tree.heading('id', text='ID')
        self.tree.heading('card_number', text='Número de Tarjeta')
        self.tree.heading('balance', text='Monto')
        self.tree.heading('status', text='Estado')
        self.tree.heading('created_at', text='Creado')
        
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('card_number', width=180)  # Un poco más ancho para diferentes longitudes
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
            
            # Obtener el número de tarjeta (formateado para mostrar)
            card_number = getattr(card, 'card_number', '')
            
            # Formatear para mostrar según la longitud
            if len(card_number) >= 4:
                # Mostrar solo los últimos 4 dígitos por seguridad
                display_number = f"**** **** **** {card_number[-4:]}"
            else:
                display_number = card_number
            
            # Insertar en el treeview
            item_id = self.tree.insert('', tk.END, values=(
                card.id, 
                display_number,
                balance_str,
                '✅ Activa' if getattr(card, 'is_active', True) else '❌ Inactiva',
                created_at
            ))