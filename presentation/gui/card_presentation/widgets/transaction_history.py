import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import traceback

class TransactionHistoryPanel(ttk.Frame):
    """Panel optimizado para visualizar historial de transacciones"""
    
    def __init__(self, parent, card_transaction_service):
        super().__init__(parent)
        self.card_transaction_service = card_transaction_service
        self.current_card_id = None
        self.transactions = []
        
        self._setup_styles()
        self._create_widgets()
    
    def _setup_styles(self):
        """Configura estilos minimalistas"""
        style = ttk.Style()
        style.configure('Credit.TLabel', foreground='green')
        style.configure('Debit.TLabel', foreground='red')

        style.configure('Credit.Treeview', background='#e8f5e9')  
        style.configure('Debit.Treeview', background='#ffebee')
    
    def _create_widgets(self):
        """Crea la interfaz optimizada """
        # Configurar grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  
        
        filter_frame = ttk.Frame(self)
        filter_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        periods = [
            ("Hoy", 0),
            ("Ayer", 1),
            ("Semana", 7),
            ("Mes", 30),
            ("3 Meses", 90)
        ]
        
        for text, days in periods:
            btn = ttk.Button(
                filter_frame,
                text=text,
                command=lambda d=days: self._apply_period_filter(d)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # 2. Área de transacciones - ROW 1
        list_frame = ttk.LabelFrame(self, text="Transacciones", padding="10")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview con scrollbars
        columns = ('id', 'fecha', 'tipo', 'monto', 'saldo')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=12,
            selectmode='browse'
        )
        
        # Configurar columnas
        column_configs = [
            ('id', 'ID', 60, 'center'),
            ('fecha', 'Fecha', 140, 'center'),
            ('tipo', 'Tipo', 100, 'center'),
            ('monto', 'Monto', 100, 'center'),
            ('saldo', 'Saldo', 120, 'center')
        ]
        
        for col_id, heading, width, anchor in column_configs:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor) # type: ignore
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.tag_configure('credit', background="#65a87f")  
        self.tree.tag_configure('debit', background="#813B45")

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # 3. Panel de estadísticas - ROW 2
        stats_frame = ttk.LabelFrame(self, text="Resumen", padding="10")
        stats_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        
        # Crear estadísticas
        self.stats_vars = {
            'total': tk.StringVar(value="$0.00"),
            'creditos': tk.StringVar(value="$0.00"),
            'debitos': tk.StringVar(value="$0.00"),
            'count': tk.StringVar(value="0")
        }
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        labels = [
            ("Total:", self.stats_vars['total']),
            ("Créditos:", self.stats_vars['creditos']),
            ("Débitos:", self.stats_vars['debitos']),
            ("Transacciones:", self.stats_vars['count'])
        ]
        
        for i, (text, var) in enumerate(labels):
            ttk.Label(stats_grid, text=text).grid(row=0, column=i*2, sticky='w', padx=(0, 5))
            ttk.Label(stats_grid, textvariable=var, font=('Arial', 9, 'bold')).grid(
                row=0, column=i*2+1, sticky='w', padx=(0, 20)
            )
        
        # 4. Botones de acción - ROW 3
        action_frame = ttk.Frame(self)
        action_frame.grid(row=3, column=0, sticky='ew')
        
        ttk.Button(
            action_frame,
            text="Actualizar",
            command=self._refresh_history
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            action_frame,
            text="Detalles",
            command=self._view_details
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            action_frame,
            text="Exportar",
            command=self._export_history
        ).pack(side=tk.LEFT, padx=2)
        
        # Bindings
        self.tree.bind('<Double-Button-1>', lambda e: self._view_details())
    
    def load_card_history(self, card_id):
        """Carga el historial de una tarjeta"""
        self.current_card_id = card_id
        self._refresh_history()
    
    def _refresh_history(self):
        """Actualiza el historial"""
        if not self.current_card_id:
            return
        
        try:
            # Obtener transacciones del servicio
            from application.dtos.card_transaction_dtos import GetCardTransactionsRequest
            
            # Usar rango por defecto (últimos 30 días)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            request = GetCardTransactionsRequest(
                card_id=self.current_card_id,
                start_date=start_date,
                end_date=end_date
            )
            
            response = self.card_transaction_service.get_transactions(request)
            if response and response.success:
                self.transactions = response.transactions
                self._display_transactions()
                self._update_statistics(response)
            else:
                messagebox.showerror("Error", "No se pudieron cargar las transacciones")
                traceback.print_exc()
            
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")
    
    def _display_transactions(self):
        """Muestra transacciones en el treeview"""
        self.tree.delete(*self.tree.get_children())
        
        if not self.transactions:
            return
        
        # Ordenar por fecha (más reciente primero)
        sorted_trans = sorted(self.transactions, 
                            key=lambda x: x.operation_date, 
                            reverse=True)
        
        for trans in sorted_trans:
            # Formatear valores
            amount = trans.amount
            amount_str = f"${amount:,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"
            
            # Determinar tipo
            trans_type = self._format_type(trans.transaction_type)
            
            tag = 'credit' if amount > 0 else 'debit'
            # Insertar
            self.tree.insert("", tk.END, values=(
                trans.id,
                trans.operation_date.strftime("%Y-%m-%d %H:%M"),
                trans_type,
                amount_str,
                f"${trans.previous_balance:,.2f}" 
            ), tags=(tag,))
    
    def _update_statistics(self, response):
        """Actualiza estadísticas"""
        self.stats_vars['total'].set(f"${response.net_movement:,.2f}")
        self.stats_vars['creditos'].set(f"${response.total_credits:,.2f}")
        self.stats_vars['debitos'].set(f"${response.total_debits:,.2f}")
        self.stats_vars['count'].set(str(response.total_count))
    
    def _apply_period_filter(self, days):
        """Aplica filtro de período REAL"""
        if not self.current_card_id:
            return
        
        try:
            from application.dtos.card_transaction_dtos import GetCardTransactionsRequest
            
            end_date = datetime.now()
            
            if days == 0:  # "Hoy"
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # Ayer, Semana, Mes, 3 Meses
                start_date = end_date - timedelta(days=days)
            
            # Para "Ayer", necesitamos ajustar el rango completo
            if days == 1:
                # Ayer completo (desde 00:00 hasta 23:59 de ayer)
                start_date = end_date - timedelta(days=1)
                start_date = start_date.replace(hour=0, minute=0, second=0)
                end_date = start_date.replace(hour=23, minute=59, second=59)
            else:
                # Para otros períodos, incluir hasta ahora
                end_date = end_date.replace(hour=23, minute=59, second=59)
            
            request = GetCardTransactionsRequest(
                card_id=self.current_card_id,
                start_date=start_date,
                end_date=end_date
            )
            
            response = self.card_transaction_service.get_transactions(request)
            
            if response and response.success:
                self.transactions = response.transactions
                self._display_transactions()
                self._update_statistics(response)
            else:
                messagebox.showerror("Error", "No se pudieron cargar las transacciones")
                traceback.print_exc()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtro: {str(e)}")
    
    def _view_details(self):
        """Muestra detalles de transacción seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Seleccionar", "Selecciona una transacción")
            return
        
        item = self.tree.item(selection[0])
        trans_id = item['values'][0]
        
        # Buscar transacción completa
        transaction = next((t for t in self.transactions if t.id == trans_id), None)
        
        if transaction:
            self._show_transaction_details(transaction)
    
    def _show_transaction_details(self, transaction):
        """Muestra diálogo de detalles"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Detalles Transacción #{transaction.id}")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Centrar diálogo
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Contenido
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        saldo_anterior = transaction.previous_balance - transaction.amount

        details = [
            ("ID:", transaction.id),
            ("Fecha:", transaction.operation_date.strftime("%Y-%m-%d %H:%M:%S")),
            ("Tipo:", self._format_type(transaction.transaction_type)),
            ("Monto:", f"${transaction.amount:,.2f}"),
            ("Saldo Anterior:", f"${saldo_anterior:,.2f}" if saldo_anterior > 0 else 0 ),
            ("Nuevo Saldo:", f"${transaction.previous_balance:,.2f}"),
            ("Descripción:", transaction.description or "Sin descripción")
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=i, column=0, sticky='w', pady=2
            )
            ttk.Label(frame, text=value).grid(
                row=i, column=1, sticky='w', pady=2, padx=(10, 0)
            )
        
        # Botón cerrar
        ttk.Button(
            dialog,
            text="Cerrar",
            command=dialog.destroy
        ).pack(pady=(10, 0))
    
    def _export_history(self):
        """Exporta historial"""
        if not self.current_card_id:
            messagebox.showwarning("Exportar", "Selecciona una tarjeta primero")
            return
        
        # Diálogo simple de exportación
        dialog = tk.Toplevel(self)
        dialog.title("Exportar Historial")
        dialog.geometry("300x200")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Formato:").pack(anchor='w', pady=(0, 5))
        
        format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(frame, text="CSV", variable=format_var, value="csv").pack(anchor='w')
        ttk.Radiobutton(frame, text="Excel", variable=format_var, value="excel").pack(anchor='w')
        ttk.Radiobutton(frame, text="PDF", variable=format_var, value="pdf").pack(anchor='w')
        
        def do_export():
            format = format_var.get()
            messagebox.showinfo("Exportar", 
                              f"Historial exportado como {format.upper()}")
            dialog.destroy()
        
        ttk.Button(
            frame,
            text="Exportar",
            command=do_export
        ).pack(pady=(20, 0))
    
    def _format_type(self, trans_type):
        """Formatea tipo de transacción"""
        type_map = {
            'RECHARGE': 'Recarga',
            'DIET_ADVANCE': 'Adelanto',
            'PAYMENT': 'Pago',
            'REFUND': 'Reembolso',
            'ADJUSTMENT': 'Ajuste'
        }
        return type_map.get(trans_type, trans_type)