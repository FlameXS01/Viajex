import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkinter import messagebox
from typing import List, Dict, Any

from application.services.diet_service import DietAppService


class DietForm(ttk.Frame):
    """
    Formulario compacto para crear y editar dietas
    """
    
    def __init__(self, parent, user_service, card_service, diet_service: DietAppService, diet=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_service = user_service
        self.card_service = card_service
        self.diet_service = diet_service
        self.diet = diet
        self.is_edit_mode = diet is not None
        self.current_diet_id = diet.id if diet else None
        self.acumulative_price = 0
        self.main_frame = None
        
        self.users = user_service.get_all_users() if user_service else []
        self.cards = card_service.get_aviable_cards() if card_service else []
        self.valid_cards = []
        
        self._setup_variables()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._create_widgets()
        self._setup_bindings()
        
        if diet:
            self._load_diet_data()

    def _setup_variables(self):
        """Configura las variables de control del formulario"""
        self.description_var = tk.StringVar()
        self.is_local_var = tk.BooleanVar(value=True)
        self.diet_type_var = tk.StringVar(value="GROUP")
        
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.req_date_var = tk.StringVar()
        
        self.service_vars = {
            "breakfast_count": tk.IntVar(value=0),
            "lunch_count": tk.IntVar(value=0),
            "dinner_count": tk.IntVar(value=0),
            "accommodation_count": tk.IntVar(value=0)
        }
        
        self.payment_method_var = tk.StringVar(value="CASH")
        self.selected_card_var = tk.StringVar()
        self.search_var = tk.StringVar()

    def _create_widgets(self):
        """Crea todos los widgets del formulario de forma compacta"""
        main_frame = ttk.Frame(self, padding=5)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Configurar filas compactas
        for i in range(6):
            main_frame.rowconfigure(i, weight=0)
        
        self._create_basic_info_section(main_frame)
        self._create_user_selection_section(main_frame)
        self._create_diet_details_section(main_frame)
        self._create_payment_section(main_frame)

        self.main_frame = main_frame

    def _create_basic_info_section(self, parent):
        basic_info_frame = ttk.LabelFrame(
            parent, 
            text="📋 Información Básica", 
            padding=8
        )
        basic_info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        basic_info_frame.columnconfigure(1, weight=1)

        ttk.Label(basic_info_frame, text="Descripción:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 3)
        )
        
        self.description_entry = ttk.Entry(
            basic_info_frame, 
            textvariable=self.description_var,
            width=45,
            font=('Arial', 9)
        )
        self.description_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 3), padx=(5, 0))
        
        type_frame = ttk.Frame(basic_info_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(3, 0))
        
        ttk.Label(type_frame, text="Tipo:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )

        self.local_check = ttk.Checkbutton(
            type_frame, 
            text="Local", 
            variable=self.is_local_var
        )
        self.local_check.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))

        self.individual_radio = ttk.Radiobutton(
            type_frame, 
            text="Individual", 
            variable=self.diet_type_var, 
            value="INDIVIDUAL", 
            command=self._on_diet_type_change
        )
        self.individual_radio.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        self.group_radio = ttk.Radiobutton(
            type_frame, 
            text="Grupal", 
            variable=self.diet_type_var, 
            value="GROUP", 
            command=self._on_diet_type_change
        )
        self.group_radio.grid(row=0, column=3, sticky=tk.W)

        if self.is_edit_mode:
            self.local_check.config(state='disabled')
            self.individual_radio.config(state='disabled')
            self.group_radio.config(state='disabled')

    def _create_user_selection_section(self, parent):
        self.users_frame = ttk.LabelFrame(
            parent, 
            text="👤 Usuario" if self.is_edit_mode else "👥 Usuarios", 
            padding=8
        )
        self.users_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.users_frame.columnconfigure(0, weight=1)
        self.users_frame.rowconfigure(0, weight=1)

        if self.is_edit_mode:
            # En modo edición: mostrar solo el combobox para seleccionar un usuario
            edit_frame = ttk.Frame(self.users_frame)
            edit_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
            edit_frame.columnconfigure(1, weight=1)
            
            ttk.Label(edit_frame, text="Usuario:").grid(
                row=0, column=0, sticky=tk.W, padx=(0, 5)
            )
            
            user_values = [f"{user.fullname} ({user.ci})" for user in self.users]
            self.edit_user_combo = ttk.Combobox(
                edit_frame, 
                values=user_values, 
                state="readonly",
                height=6,
                font=('Arial', 9),
                width=40
            )
            self.edit_user_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
            
            if user_values:
                self.edit_user_combo.set(user_values[0])
        else:
            # Modo creación: mostrar todo el sistema de selección
            self.selection_container = ttk.Frame(self.users_frame)
            self.selection_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.selection_container.columnconfigure(0, weight=1)
            self.selection_container.rowconfigure(0, weight=1)

            self.view_only_container = ttk.Frame(self.users_frame)
            self.view_only_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.view_only_container.columnconfigure(0, weight=1)
            self.view_only_container.rowconfigure(1, weight=1)
            
            ttk.Label(self.view_only_container, text="Usuarios:").grid(
                row=0, column=0, sticky=tk.W, pady=(0, 3)
            )
            
            columns = ("nombre", "ci")
            self.users_treeview = ttk.Treeview(
                self.view_only_container, 
                columns=columns, 
                show="headings", 
                height=3,
                selectmode="none"
            )
            
            self.users_treeview.heading("nombre", text="Nombre")
            self.users_treeview.heading("ci", text="Cédula")
            self.users_treeview.column("nombre", width=180, minwidth=180)
            self.users_treeview.column("ci", width=100, minwidth=100)
            
            self.users_treeview.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            tree_scrollbar = ttk.Scrollbar(
                self.view_only_container, 
                orient=tk.VERTICAL, 
                command=self.users_treeview.yview
            )
            tree_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
            self.users_treeview.configure(yscrollcommand=tree_scrollbar.set)

            self.individual_frame = self._create_individual_selection()
            self.individual_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.group_frame = self._create_group_selection()
            self.group_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.view_only_container.grid_remove()
            self.selection_container.grid()   

    def _create_individual_selection(self):
        frame = ttk.Frame(self.selection_container)
        frame.columnconfigure(0, weight=1)
        
        ttk.Label(frame, text="Usuario:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 3)
        )
        
        user_values = [f"{user.fullname} ({user.ci})" for user in self.users]
        self.user_combo = ttk.Combobox(
            frame, 
            values=user_values, 
            state="readonly",
            textvariable=tk.StringVar(),
            height=6,
            font=('Arial', 9)
        )
        self.user_combo.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        if user_values:
            self.user_combo.set(user_values[0])
            
        return frame

    def _create_group_selection(self):
        frame = ttk.Frame(self.selection_container)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Búsqueda
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 3))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Buscar:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25,
            font=('Arial', 9)
        )
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Listas y botones
        lists_frame = ttk.Frame(frame)
        lists_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(3, 0))
        lists_frame.columnconfigure(0, weight=1)
        lists_frame.columnconfigure(2, weight=1)
        lists_frame.rowconfigure(0, weight=1)

        # Lista de disponibles
        available_frame = ttk.Frame(lists_frame)
        available_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2))
        available_frame.columnconfigure(0, weight=1)
        available_frame.rowconfigure(1, weight=1)
        
        ttk.Label(available_frame, text="Disponibles:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2)
        )
        
        self.available_listbox = tk.Listbox(
            available_frame, 
            height=5, 
            selectmode=tk.SINGLE,
            font=('Arial', 9)
        )
        self.available_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        available_scrollbar = ttk.Scrollbar(
            available_frame, 
            orient=tk.VERTICAL, 
            command=self.available_listbox.yview
        )
        available_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.available_listbox.configure(yscrollcommand=available_scrollbar.set)

        # Botones de transferencia
        buttons_frame = ttk.Frame(lists_frame)
        buttons_frame.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=2)
        
        ttk.Button(
            buttons_frame, 
            text=">", 
            command=self._add_selected_user,
            width=3
        ).pack(pady=1)
        
        ttk.Button(
            buttons_frame, 
            text="<", 
            command=self._remove_selected_user,
            width=3
        ).pack(pady=1)
        
        ttk.Button(
            buttons_frame, 
            text=">>", 
            command=self._add_all_users,
            width=3
        ).pack(pady=1)
        
        ttk.Button(
            buttons_frame, 
            text="<<", 
            command=self._remove_all_users,
            width=3
        ).pack(pady=1)

        # Lista de seleccionados
        selected_frame = ttk.Frame(lists_frame)
        selected_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 0))
        selected_frame.columnconfigure(0, weight=1)
        selected_frame.rowconfigure(1, weight=1)
        
        ttk.Label(selected_frame, text="Seleccionados:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2)
        )
        
        self.selected_listbox = tk.Listbox(
            selected_frame, 
            height=5, 
            selectmode=tk.SINGLE,
            font=('Arial', 9)
        )
        self.selected_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        selected_scrollbar = ttk.Scrollbar(
            selected_frame, 
            orient=tk.VERTICAL, 
            command=self.selected_listbox.yview
        )
        selected_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.selected_listbox.configure(yscrollcommand=selected_scrollbar.set)

        # Guardar la lista completa de usuarios
        self.all_users_strings = []
        for user in self.users:
            user_text = f"{user.fullname} ({user.ci})"
            self.all_users_strings.append(user_text)
            self.available_listbox.insert(tk.END, user_text)
        
        self.all_users = self.users
        
        # Configurar búsqueda en tiempo real
        self.search_var.trace_add("write", lambda *args: self._filter_users())
        
        return frame

    def _filter_users(self):
        """Filtra la lista de usuarios disponibles"""
        search_text = self.search_var.get().lower().strip()
        
        selected_users = set(self.selected_listbox.get(0, tk.END))
        
        self.available_listbox.delete(0, tk.END)
        
        for user_text in self.all_users_strings:
            if user_text not in selected_users:
                if not search_text or search_text in user_text.lower():
                    self.available_listbox.insert(tk.END, user_text)

    def _create_diet_details_section(self, parent):
        details_frame = ttk.LabelFrame(
            parent, 
            text="📅 Detalles", 
            padding=8
        )
        details_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        details_frame.columnconfigure(1, weight=1)

        # Fechas
        dates_frame = ttk.Frame(details_frame)
        dates_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Configurar columnas para 3 grupos (etiqueta + entrada)
        dates_frame.columnconfigure(1, weight=0)
        dates_frame.columnconfigure(3, weight=0)
        dates_frame.columnconfigure(5, weight=0)

        # Grupo 1: Fecha de Inicio
        ttk.Label(dates_frame, text="Inicio:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 3)
        )
        
        self.start_date_entry = ttk.Entry(
            dates_frame, 
            textvariable=self.start_date_var,
            width=12,
            font=('Arial', 9)
        )
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        
        default_start = datetime.now().strftime("%d/%m/%Y")
        self.start_date_var.set(default_start)

        # Grupo 2: Fecha de Fin
        ttk.Label(dates_frame, text="Fin:").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 3)
        )
        
        self.end_date_entry = ttk.Entry(
            dates_frame, 
            textvariable=self.end_date_var,
            width=12,
            font=('Arial', 9)
        )
        self.end_date_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 15))
        
        default_end = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        self.end_date_var.set(default_end)

        # Grupo 3: Fecha de Solicitud
        ttk.Label(dates_frame, text="Solicitud:").grid(
            row=0, column=4, sticky=tk.W, padx=(0, 3)
        )
        
        self.req_date_entry = ttk.Entry(
            dates_frame, 
            textvariable=self.req_date_var,
            width=12,
            font=('Arial', 9)
        )
        self.req_date_entry.grid(row=0, column=5, sticky=tk.W)
        
        default_req = datetime.now().strftime("%d/%m/%Y")  # Fecha actual
        self.req_date_var.set(default_req)

        # Servicios
        services_frame = ttk.Frame(details_frame)
        services_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        services_config = [
            ("Desayunos:", "breakfast_count"),
            ("Almuerzos:", "lunch_count"), 
            ("Comidas:", "dinner_count"),
            ("Alojamientos:", "accommodation_count")
        ]
        
        for i, (label, var_name) in enumerate(services_config):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(services_frame, text=label).grid(
                row=row, column=col, sticky=tk.W, pady=2, padx=(0, 3)
            )
            
            spinbox = ttk.Spinbox(
                services_frame, 
                from_=0, 
                to=999,
                textvariable=self.service_vars[var_name],
                width=6,
                font=('Arial', 9)
            )
            spinbox.grid(row=row, column=col + 1, sticky=tk.W, pady=2, padx=(0, 10))

    def _create_payment_section(self, parent):
        payment_frame = ttk.LabelFrame(
            parent, 
            text="💳 Pago", 
            padding=8
        )
        payment_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        payment_frame.columnconfigure(1, weight=1)

        method_frame = ttk.Frame(payment_frame)
        method_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        method_frame.columnconfigure(2, weight=1)

        ttk.Label(method_frame, text="Método:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )

        cash_radio = ttk.Radiobutton(
            method_frame, 
            text="Efectivo", 
            variable=self.payment_method_var, 
            value="CASH", 
            command=self._on_payment_method_change
        )
        cash_radio.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        card_radio = ttk.Radiobutton(
            method_frame, 
            text="Tarjeta", 
            variable=self.payment_method_var, 
            value="CARD", 
            command=self._on_payment_method_change
        )
        card_radio.grid(row=0, column=2, sticky=tk.W)

        self._update_valid_cards()
        card_values = [f"{card.card_number} - {card.card_pin}" for card in self.valid_cards]
        self.card_combo = ttk.Combobox(
            method_frame,
            values=card_values,
            textvariable=self.selected_card_var,
            state="readonly",
            width=20,
            font=('Arial', 9)
        )
        self.card_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))

        if card_values:
            self.card_combo.set(card_values[0])

    def _setup_bindings(self):
        self.start_date_entry.bind('<FocusOut>', self._validate_dates)
        self.end_date_entry.bind('<FocusOut>', self._validate_dates)
        self.service_vars["accommodation_count"].trace_add("write", self._on_price_change)
        self.is_local_var.trace_add("write", self._on_price_change)

    def _on_price_change(self, *args):
        """Actualiza las tarjetas válidas cuando cambia cualquier factor de precio"""
        self._update_valid_cards()
        
        if hasattr(self, 'card_combo') and self.payment_method_var.get() == "CARD":
            card_values = [f"{card.card_number} - {card.card_pin}" for card in self.valid_cards]
            current_selection = self.selected_card_var.get()
            self.card_combo['values'] = card_values
            
            if card_values:
                if current_selection in card_values:
                    self.card_combo.set(current_selection)
                else:
                    self.card_combo.set(card_values[0])
            else:
                self.card_combo.set('')
                if not self.is_edit_mode and self.acumulative_price > 0:
                    messagebox.showwarning(
                        "Tarjetas Insuficientes", 
                        f"No hay tarjetas con saldo suficiente (${self.acumulative_price:.2f} requeridos)"
                    )

    def _update_valid_cards(self):
        """Actualiza la lista de tarjetas válidas basadas en el precio acumulado"""
        self._calculate_acumulative_price()
        self.valid_cards = [card for card in self.cards if card.balance >= self.acumulative_price]

    def _calculate_acumulative_price(self):
        """Calcula el precio acumulado para los alojamientos"""
        if self.is_edit_mode:
            total_request_user = 1
        else:
            if self.diet_type_var.get() == "INDIVIDUAL":
                total_request_user = 1
            else:
                total_request_user = self.selected_listbox.size()
        
        total_acomodation_service = total_request_user * self.service_vars["accommodation_count"].get()
        
        try:
            if self.is_local_var.get():
                price = self.diet_service.get_diet_service_by_local(True).accommodation_card_price
            else:
                price = self.diet_service.get_diet_service_by_local(False).accommodation_card_price
        except:
            price = 0
        
        self.acumulative_price = total_acomodation_service * price

    def _on_diet_type_change(self):
        if self.diet_type_var.get() == "INDIVIDUAL":
            self.individual_frame.grid()
            self.group_frame.grid_remove()
            self.user_combo.config(state="readonly")
        else:
            self.individual_frame.grid_remove()
            self.group_frame.grid()
        
        self._on_price_change()
        
        new_title = "👤 Usuario" if self.diet_type_var.get() == "INDIVIDUAL" else "👥 Usuarios"
        self.users_frame.configure(text=new_title)

    def _on_payment_method_change(self):
        if self.payment_method_var.get() == "CARD":
            self.card_combo.config(state='readonly')
            self._on_price_change()
        else:
            self.card_combo.config(state='disabled')

    def _add_selected_user(self):
        selection = self.available_listbox.curselection()
        if selection:
            user_text = self.available_listbox.get(selection[0])
            self.available_listbox.delete(selection[0])
            self.selected_listbox.insert(tk.END, user_text)
            self._on_price_change()
            if self.search_var.get():
                self._filter_users()

    def _remove_selected_user(self):
        selection = self.selected_listbox.curselection()
        if selection:
            user_text = self.selected_listbox.get(selection[0])
            self.selected_listbox.delete(selection[0])
            if not self.search_var.get() or self.search_var.get().lower() in user_text.lower():
                self.available_listbox.insert(tk.END, user_text)
            self._on_price_change()
            if self.search_var.get():
                self._filter_users()

    def _add_all_users(self):
        available_users = list(self.available_listbox.get(0, tk.END))
        for user in available_users:
            self.selected_listbox.insert(tk.END, user)
        self.available_listbox.delete(0, tk.END)
        self._on_price_change()

    def _remove_all_users(self):
        selected_users = list(self.selected_listbox.get(0, tk.END))
        for user in selected_users:
            if not self.search_var.get() or self.search_var.get().lower() in user.lower():
                self.available_listbox.insert(tk.END, user)
        self.selected_listbox.delete(0, tk.END)
        self._on_price_change()
        if self.search_var.get():
            self._filter_users()

    def _validate_dates(self, event=None):
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            if start_date and end_date:
                datetime.strptime(start_date, "%d/%m/%Y")
                datetime.strptime(end_date, "%d/%m/%Y")
        except ValueError:
            pass

    def _load_diet_data(self):
        if not self.diet:
            return
            
        self.description_var.set(self.diet.description)
        self.is_local_var.set(self.diet.is_local)
        self.diet_type_var.set("GROUP" if self.diet.is_group else "INDIVIDUAL")
        
        if self.diet.start_date:
            self.start_date_var.set(self.diet.start_date.strftime("%d/%m/%Y"))
        if self.diet.end_date:
            self.end_date_var.set(self.diet.end_date.strftime("%d/%m/%Y"))
        if self.diet.created_at:
            self.req_date_var.set(self.diet.created_at.strftime("%d/%m/%Y"))

        self.service_vars["breakfast_count"].set(self.diet.breakfast_count)
        self.service_vars["lunch_count"].set(self.diet.lunch_count)
        self.service_vars["dinner_count"].set(self.diet.dinner_count)
        self.service_vars["accommodation_count"].set(self.diet.accommodation_count)
        
        self.payment_method_var.set(self.diet.accommodation_payment_method)
        self._on_payment_method_change()
        
        if self.diet.accommodation_card_id and self.cards:
            card = next((c for c in self.cards if c.id == self.diet.accommodation_card_id), None)
            if card:
                self.selected_card_var.set(f"{card.card_number} - {card.card_pin}")

        # Cargar usuario actual en modo edición
        if self.is_edit_mode:
            user = next((u for u in self.users if u.id == self.diet.request_user_id), None)
            if user:
                user_display = f"{user.fullname} ({user.ci})"
                if hasattr(self, 'edit_user_combo'):
                    current_values = list(self.edit_user_combo['values'])
                    if user_display in current_values:
                        self.edit_user_combo.set(user_display)
                    else:
                        # Si el usuario no está en la lista, agregarlo
                        new_values = list(current_values) + [user_display]
                        self.edit_user_combo['values'] = new_values
                        self.edit_user_combo.set(user_display)
        else:
            # Código original para modo creación
            if not self.is_edit_mode:
                user_ids = [self.diet.request_user_id]
                
                if self.diet.is_group:
                    for user_id in user_ids:
                        user = next((u for u in self.users if u.id == user_id), None)
                        if user:
                            user_text = f"{user.fullname} ({user.ci})"
                            available_items = list(self.available_listbox.get(0, tk.END))
                            if user_text in available_items:
                                index = available_items.index(user_text)
                                self.available_listbox.delete(index)
                                self.selected_listbox.insert(tk.END, user_text)
                else:
                    user = next((u for u in self.users if u.id == user_ids[0]), None)
                    if user:
                        user_display = f"{user.fullname} ({user.ci})"
                        current_values = list(self.user_combo['values'])
                        if user_display in current_values:
                            self.user_combo.set(user_display)
                        else:
                            new_values = list(current_values) + [user_display]
                            self.user_combo['values'] = new_values
                            self.user_combo.set(user_display)

            if not self.is_edit_mode:
                self._on_diet_type_change()

    def get_form_data(self):
        """Obtiene todos los datos del formulario en un diccionario"""
        selected_user_ids = []
        
        if self.is_edit_mode:
            # En modo edición: obtener del combobox especial
            if hasattr(self, 'edit_user_combo'):
                selected_user = self.edit_user_combo.get()
                if selected_user:
                    user = next((u for u in self.users if f"{u.fullname} ({u.ci})" == selected_user), None)
                    if user:
                        selected_user_ids = [user.id]
            else:
                # Fallback: usar el usuario original
                selected_user_ids = [self.diet.request_user_id]
        else:
            # Modo creación: lógica original
            if self.diet_type_var.get() == "INDIVIDUAL":
                selected_user = self.user_combo.get()
                if selected_user:
                    user = next((u for u in self.users if f"{u.fullname} ({u.ci})" == selected_user), None)
                    if user:
                        selected_user_ids = [user.id]
            else:
                selected_count = self.selected_listbox.size()
                for i in range(selected_count):
                    user_text = self.selected_listbox.get(i)
                    user = next((u for u in self.users if f"{u.fullname} ({u.ci})" == user_text), None)
                    if user:
                        selected_user_ids.append(user.id)
        
        selected_card = self.selected_card_var.get()
        card_id = None
        if selected_card and self.payment_method_var.get() == "CARD":
            card = next((c for c in self.cards if f"{c.card_number} - {c.card_pin}" == selected_card), None)
            card_id = card.id if card else None
        
        return {
            "description": self.description_var.get(),
            "is_local": self.is_local_var.get(),
            "is_group": self.diet_type_var.get() == "GROUP",
            "start_date": self.start_date_var.get(),
            "end_date": self.end_date_var.get(),
            "created_at": self.req_date_var.get(),
            "breakfast_count": self.service_vars["breakfast_count"].get(),
            "lunch_count": self.service_vars["lunch_count"].get(),
            "dinner_count": self.service_vars["dinner_count"].get(),
            "accommodation_count": self.service_vars["accommodation_count"].get(),
            "accommodation_payment_method": self.payment_method_var.get(),
            "accommodation_card_id": card_id,
            "user_ids": selected_user_ids
        } 
    
    def validate_form(self):
        """
        Valida todos los campos del formulario
        
        Returns:
            tuple: (is_valid, errors)
        """
        errors = []
        data = self.get_form_data()
        
        if not data["description"].strip():
            errors.append("La descripción es obligatoria")
            
        try:
            start_date = datetime.strptime(data["start_date"], "%d/%m/%Y")
            end_date = datetime.strptime(data["end_date"], "%d/%m/%Y")
            
            if end_date < start_date:
                errors.append("La fecha de fin no puede ser anterior a la fecha de inicio")
        except ValueError:
            errors.append("Formato de fecha inválido. Use DD/MM/YYYY")
            
        if not data["user_ids"]:
            errors.append("Debe seleccionar al menos un usuario")
            
        if data["accommodation_payment_method"] == "CARD" and not data["accommodation_card_id"]:
            errors.append("Debe seleccionar una tarjeta cuando el método de pago es tarjeta")

        return len(errors) == 0, errors