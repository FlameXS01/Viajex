import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


class DietForm(ttk.Frame):
    def __init__(self, parent, user_service, card_service, diet=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_service = user_service
        self.card_service = card_service
        self.diet = diet
        self.is_edit_mode = diet is not None
        self.current_diet_id = diet.id if diet else None
        
        self.users = user_service.get_all_users() if user_service else []
        self.cards = card_service.get_all_cards() if card_service else []
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._create_widgets()
        if diet:
            self._load_diet_data()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)  

        title_text = "Editar Dieta" if self.is_edit_mode else "Crear Nueva Dieta"
        title_label = ttk.Label(main_frame, text=title_text, font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        basic_info_frame = ttk.LabelFrame(main_frame, text="Información Básica", padding=10)
        basic_info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        basic_info_frame.columnconfigure(1, weight=1)

        desc_frame = ttk.Frame(basic_info_frame)
        desc_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        desc_frame.columnconfigure(1, weight=1)
        
        ttk.Label(desc_frame, text="Descripción:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.description_entry = ttk.Entry(desc_frame, width=50)  
        self.description_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        type_frame = ttk.Frame(basic_info_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(type_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.is_local_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(type_frame, text="Local", variable=self.is_local_var).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        self.diet_type_var = tk.StringVar(value="INDIVIDUAL")
        ttk.Radiobutton(type_frame, text="Individual", variable=self.diet_type_var, 
                       value="INDIVIDUAL", command=self._on_diet_type_change).grid(row=0, column=2, sticky=tk.W, padx=(0, 15))
        ttk.Radiobutton(type_frame, text="Grupal", variable=self.diet_type_var, 
                       value="GROUP", command=self._on_diet_type_change).grid(row=0, column=3, sticky=tk.W)

        users_frame = ttk.LabelFrame(main_frame, text="Selección de Usuarios", padding=10)
        users_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        users_frame.columnconfigure(0, weight=1)

        self.selection_container = ttk.Frame(users_frame)
        self.selection_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.selection_container.columnconfigure(0, weight=1)

        # Frame individual 
        self.individual_frame = ttk.Frame(self.selection_container, width=650)  
        self.individual_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.individual_frame.columnconfigure(0, weight=1)
        self.individual_frame.grid_propagate(False)  
        
        ttk.Label(self.individual_frame, text="Usuario:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.user_combo = ttk.Combobox(self.individual_frame, 
                                     values=[f"{user.fullname} ({user.ci})" for user in self.users], 
                                     state="readonly", width=60)
        self.user_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Frame grupal
        self.multi_selection_frame = ttk.Frame(self.selection_container, width=650, height=120)
        self.multi_selection_frame.columnconfigure(0, weight=1)
        self.multi_selection_frame.grid_propagate(False)  

        lists_frame = ttk.Frame(self.multi_selection_frame)
        lists_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        lists_frame.columnconfigure(0, weight=1)
        lists_frame.columnconfigure(2, weight=1)

        ttk.Label(lists_frame, text="Disponibles:").grid(row=0, column=0, sticky=tk.W, pady=(0, 2))

        listbox_frame_left = ttk.Frame(lists_frame)
        listbox_frame_left.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        listbox_frame_left.columnconfigure(0, weight=1)
        listbox_frame_left.rowconfigure(0, weight=1)
        
        self.available_users_listbox = tk.Listbox(listbox_frame_left, height=6, width=35, selectmode=tk.SINGLE)
        self.available_users_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        available_scrollbar = ttk.Scrollbar(listbox_frame_left, orient=tk.VERTICAL, command=self.available_users_listbox.yview)
        available_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.available_users_listbox.configure(yscrollcommand=available_scrollbar.set)

        buttons_frame = ttk.Frame(lists_frame)
        buttons_frame.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=5)
        
        ttk.Button(buttons_frame, text="→", command=self._add_selected_user, width=3).pack(pady=2)
        ttk.Button(buttons_frame, text="←", command=self._remove_selected_user, width=3).pack(pady=2)

        ttk.Label(lists_frame, text="Seleccionados:").grid(row=0, column=2, sticky=tk.W, pady=(0, 2))

        listbox_frame_right = ttk.Frame(lists_frame)
        listbox_frame_right.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        listbox_frame_right.columnconfigure(0, weight=1)
        listbox_frame_right.rowconfigure(0, weight=1)
        
        self.selected_users_listbox = tk.Listbox(listbox_frame_right, height=6, width=35, selectmode=tk.SINGLE)
        self.selected_users_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        selected_scrollbar = ttk.Scrollbar(listbox_frame_right, orient=tk.VERTICAL, command=self.selected_users_listbox.yview)
        selected_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.selected_users_listbox.configure(yscrollcommand=selected_scrollbar.set)

        for user in self.users:
            self.available_users_listbox.insert(tk.END, f"{user.fullname} ({user.ci})")

        details_frame = ttk.LabelFrame(main_frame, text="Detalles de la Dieta", padding=10)
        details_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        details_frame.columnconfigure(1, weight=1)

        dates_frame = ttk.Frame(details_frame)
        dates_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        dates_frame.columnconfigure(1, weight=1)
        dates_frame.columnconfigure(3, weight=1)

        ttk.Label(dates_frame, text="Inicio:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.start_date_entry = ttk.Entry(dates_frame, width=15)
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        self.start_date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ttk.Label(dates_frame, text="Fin:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        self.end_date_entry = ttk.Entry(dates_frame, width=15)
        self.end_date_entry.grid(row=0, column=3, sticky=tk.W)
        tomorrow = datetime.now() + timedelta(days=1)
        self.end_date_entry.insert(0, tomorrow.strftime("%d/%m/%Y"))

        services_frame = ttk.Frame(details_frame)
        services_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        services = [
            ("Desayunos:", "breakfast_count"),
            ("Almuerzos:", "lunch_count"), 
            ("Comidas:", "dinner_count"),
            ("Alojamientos:", "accommodation_count")
        ]
        
        self.service_vars = {}
        for i, (label, name) in enumerate(services):
            row = i % 2  
            col = i // 2 * 2  
            
            ttk.Label(services_frame, text=label).grid(row=row, column=col, sticky=tk.W, pady=2, padx=(0, 5))
            
            var = tk.IntVar(value=0)
            spinbox = ttk.Spinbox(services_frame, from_=0, to=100, textvariable=var, width=10)
            spinbox.grid(row=row, column=col+1, sticky=tk.W, pady=2, padx=(0, 15))
            self.service_vars[name] = var

        payment_frame = ttk.LabelFrame(main_frame, text="Método de Pago", padding=10)
        payment_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        method_frame = ttk.Frame(payment_frame)
        method_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        method_frame.columnconfigure(3, weight=1)

        ttk.Label(method_frame, text="Método:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.payment_method_var = tk.StringVar(value="CASH")
        ttk.Radiobutton(method_frame, text="Efectivo", variable=self.payment_method_var, 
                       value="CASH", command=self._on_payment_method_change).grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        ttk.Radiobutton(method_frame, text="Tarjeta", variable=self.payment_method_var, 
                       value="CARD", command=self._on_payment_method_change).grid(row=0, column=2, sticky=tk.W, padx=(0, 15))

        self.card_combo = ttk.Combobox(method_frame, 
                                    values=[f"{card.card_number} - {card.card_pin}" for card in self.cards], 
                                    state="disabled", width=25)
        self.card_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(10, 0))

        if self.cards:
            self.card_combo.set(self.cards[0].card_number)

        self._on_diet_type_change()
        self._on_payment_method_change()

    def _on_diet_type_change(self):
        if self.diet_type_var.get() == "INDIVIDUAL":
            self.individual_frame.grid()
            self.multi_selection_frame.grid_remove()
        else:
            self.individual_frame.grid_remove()
            self.multi_selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def _add_selected_user(self):
        selection = self.available_users_listbox.curselection()
        if selection:
            user_text = self.available_users_listbox.get(selection[0])
            self.available_users_listbox.delete(selection[0])
            self.selected_users_listbox.insert(tk.END, user_text)

    def _remove_selected_user(self):
        selection = self.selected_users_listbox.curselection()
        if selection:
            user_text = self.selected_users_listbox.get(selection[0])
            self.selected_users_listbox.delete(selection[0])
            self.available_users_listbox.insert(tk.END, user_text)

    def _on_payment_method_change(self):
        if self.payment_method_var.get() == "CARD":
            self.card_combo.config(state="readonly")
        else:
            self.card_combo.config(state="disabled")

    def _load_diet_data(self):
        if not self.diet:
            return
            
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, self.diet.description)
        self.is_local_var.set(self.diet.is_local)
        self.diet_type_var.set("GROUP" if self.diet.is_group else "INDIVIDUAL")
        self._on_diet_type_change()
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, self.diet.start_date.strftime("%d/%m/%Y"))
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, self.diet.end_date.strftime("%d/%m/%Y"))
        
        self.service_vars["breakfast_count"].set(self.diet.breakfast_count)
        self.service_vars["lunch_count"].set(self.diet.lunch_count)
        self.service_vars["dinner_count"].set(self.diet.dinner_count)
        self.service_vars["accommodation_count"].set(self.diet.accommodation_count)
        
        self.payment_method_var.set(self.diet.accommodation_payment_method)
        self._on_payment_method_change()
        
        if self.diet.accommodation_card_id and self.cards:
            card = next((c for c in self.cards if c.id == self.diet.accommodation_card_id), None)
            if card:
                self.card_combo.set(f"{card.card_number} - {card.card_pin}")

        if self.diet.user_ids:
            if self.diet.is_group:
                for user_id in self.diet.user_ids:
                    user = next((u for u in self.users if u.id == user_id), None)
                    if user:
                        user_text = f"{user.fullname} ({user.ci})"
                        available_items = list(self.available_users_listbox.get(0, tk.END))
                        if user_text in available_items:
                            index = available_items.index(user_text)
                            self.available_users_listbox.delete(index)
                            self.selected_users_listbox.insert(tk.END, user_text)
            else:
                user = next((u for u in self.users if u.id == self.diet.user_ids[0]), None)
                if user:
                    self.user_combo.set(f"{user.fullname} ({user.ci})")

    def get_form_data(self):
        selected_user_ids = []
        if self.diet_type_var.get() == "INDIVIDUAL":
            selected_user = self.user_combo.get()
            if selected_user:
                user = next((u for u in self.users if f"{u.fullname} ({u.ci})" == selected_user), None)
                if user:
                    selected_user_ids = [user.id]
        else:
            selected_users_count = self.selected_users_listbox.size()
            for i in range(selected_users_count):
                user_text = self.selected_users_listbox.get(i)
                user = next((u for u in self.users if f"{u.fullname} ({u.ci})" == user_text), None)
                if user:
                    selected_user_ids.append(user.id)
        
        selected_card = self.card_combo.get()
        card_id = None
        if selected_card and self.payment_method_var.get() == "CARD":
            card = next((c for c in self.cards if f"{c.card_number} - {c.card_pin}" == selected_card), None)
            card_id = card.id if card else None
        
        return {
            "description": self.description_entry.get(),
            "is_local": self.is_local_var.get(),
            "is_group": self.diet_type_var.get() == "GROUP",
            "start_date": self.start_date_entry.get(),
            "end_date": self.end_date_entry.get(),
            "breakfast_count": self.service_vars["breakfast_count"].get(),
            "lunch_count": self.service_vars["lunch_count"].get(),
            "dinner_count": self.service_vars["dinner_count"].get(),
            "accommodation_count": self.service_vars["accommodation_count"].get(),
            "accommodation_payment_method": self.payment_method_var.get(),
            "accommodation_card_id": card_id,
            "user_ids": selected_user_ids
        }