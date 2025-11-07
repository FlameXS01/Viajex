import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from application.dtos.diet_dtos import DietCreateDTO, DietServiceResponseDTO, DietUpdateDTO
from application.services import diet_service
from application.services.card_service import CardService
from application.services.diet_service import DietAppService
from application.services.request_service import UserRequestService
from core.entities.cards import Card

class DietForm(ttk.Frame):
    """Formulario profesional para crear y editar dietas"""
    
    def __init__(self, parent, diet_service: DietAppService, user_service: UserRequestService, card_service: CardService, diet=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.diet_service = diet_service
        self.user_service = user_service
        self.card_service = card_service
        self.diet = diet
        self.is_edit_mode = diet is not None
        self.current_diet_id = diet.id if diet else None
        self.users = self.user_service.get_all_users()
        self.cards : list[Card] = self.card_service.get_all_cards()
        
        
        # Configurar el frame principal para expandirse
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Configuración de estilo
        self.style = ttk.Style()
        self._configure_styles()
        
        self._create_widgets()
        if diet:
            self._load_diet_data()

    def _configure_styles(self):
        """Configura estilos profesionales con mejor contraste"""
        # Usar el tema por defecto pero con mejoras de contraste
        self.style.configure('Title.TLabel', 
                           font=('Arial', 9, 'bold'), 
                           foreground='#000000')  # Negro puro para mejor contraste
        
        self.style.configure('Section.TLabelframe.Label',
                           font=('Arial', 9, 'bold'),
                           foreground='#000000')

    
    def _create_widgets(self):
        """Crea los widgets del formulario con diseño optimizado"""
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        # Título del formulario
        title_text = "Editar Dieta" if self.is_edit_mode else "Crear Nueva Dieta"
        title_label = ttk.Label(main_frame, 
                              text=title_text, 
                              font=('Arial', 12, 'bold'), 
                              foreground='#000000')
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # Sección: Información básica - COMPACTA
        basic_info_frame = ttk.LabelFrame(main_frame, 
                                        text="Información Básica", 
                                        padding=10)
        basic_info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        basic_info_frame.columnconfigure(1, weight=1)

        # Descripción - en una sola línea
        desc_frame = ttk.Frame(basic_info_frame)
        desc_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        desc_frame.columnconfigure(1, weight=1)
        
        ttk.Label(desc_frame, text="Descripción:", style='Title.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.description_entry = ttk.Entry(desc_frame, width=40, font=('Arial', 9))
        self.description_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Tipo de dieta - en una sola línea compacta
        type_frame = ttk.Frame(basic_info_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(type_frame, text="Tipo:", style='Title.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.is_local_var = tk.BooleanVar(value=True)
        local_cb = ttk.Checkbutton(type_frame, text="Local", variable=self.is_local_var)
        local_cb.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        self.diet_type_var = tk.StringVar(value="INDIVIDUAL")
        individual_rb = ttk.Radiobutton(type_frame, text="Individual", variable=self.diet_type_var, 
                                      value="INDIVIDUAL", command=self._on_diet_type_change)
        individual_rb.grid(row=0, column=2, sticky=tk.W, padx=(0, 15))
        
        group_rb = ttk.Radiobutton(type_frame, text="Grupal", variable=self.diet_type_var, 
                                 value="GROUP", command=self._on_diet_type_change)
        group_rb.grid(row=0, column=3, sticky=tk.W)

        # Sección: Selección de usuarios - MEJOR DISEÑO
        users_frame = ttk.LabelFrame(main_frame, 
                                   text="Selección de Usuarios", 
                                   padding=10)
        users_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        users_frame.columnconfigure(0, weight=1)

        # Frame contenedor para ambos tipos de selección
        self.selection_container = ttk.Frame(users_frame)
        self.selection_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.selection_container.columnconfigure(0, weight=1)

        # Selección individual (siempre visible pero cambia el contenido)
        self.individual_frame = ttk.Frame(self.selection_container)
        self.individual_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.individual_frame.columnconfigure(0, weight=1)
        
        ttk.Label(self.individual_frame, text="Usuario:", style='Title.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.user_combo = ttk.Combobox(self.individual_frame, 
                                     values=[f"{user.fullname} ({user.ci})" for user in self.users], 
                                     state="readonly", font=('Arial', 9))
        self.user_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Selección múltiple (oculto inicialmente)
        self.multi_selection_frame = ttk.Frame(self.selection_container)
        self.multi_selection_frame.columnconfigure(0, weight=1)
        self.multi_selection_frame.columnconfigure(2, weight=1)

        # Frame para los listboxes
        lists_frame = ttk.Frame(self.multi_selection_frame)
        lists_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        lists_frame.columnconfigure(0, weight=1)
        lists_frame.columnconfigure(2, weight=1)

        # Listbox izquierdo - Usuarios disponibles
        ttk.Label(lists_frame, text="Disponibles:", style='Title.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2))

        listbox_frame_left = ttk.Frame(lists_frame)
        listbox_frame_left.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.available_users_listbox = tk.Listbox(listbox_frame_left, 
                                                height=4,  # Más compacto
                                                width=30, 
                                                selectmode=tk.SINGLE, 
                                                font=('Arial', 8))
        self.available_users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        available_scrollbar = ttk.Scrollbar(listbox_frame_left, 
                                          orient=tk.VERTICAL, 
                                          command=self.available_users_listbox.yview)
        available_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.available_users_listbox.configure(yscrollcommand=available_scrollbar.set)

        # Botones de movimiento en el centro
        buttons_frame = ttk.Frame(lists_frame)
        buttons_frame.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=5)
        
        ttk.Button(buttons_frame, text="→", 
                 command=self._add_selected_user, width=3).pack(pady=2)
        ttk.Button(buttons_frame, text="←", 
                 command=self._remove_selected_user, width=3).pack(pady=2)

        # Listbox derecho - Usuarios seleccionados
        ttk.Label(lists_frame, text="Seleccionados:", style='Title.TLabel').grid(
            row=0, column=2, sticky=tk.W, pady=(0, 2))

        listbox_frame_right = ttk.Frame(lists_frame)
        listbox_frame_right.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.selected_users_listbox = tk.Listbox(listbox_frame_right, 
                                               height=4,  # Más compacto
                                               width=30, 
                                               selectmode=tk.SINGLE, 
                                               font=('Arial', 8))
        self.selected_users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        selected_scrollbar = ttk.Scrollbar(listbox_frame_right, 
                                         orient=tk.VERTICAL, 
                                         command=self.selected_users_listbox.yview)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.selected_users_listbox.configure(yscrollcommand=selected_scrollbar.set)

        # Poblar listbox de usuarios disponibles
        for user in self.users:
            self.available_users_listbox.insert(tk.END, f"{user.fullname} ({user.ci})")

        # Sección: Fechas y servicios - MÁS COMPACTO
        details_frame = ttk.LabelFrame(main_frame, 
                                     text="Detalles de la Dieta", 
                                     padding=10)
        details_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        details_frame.columnconfigure(1, weight=1)

        # Fechas en una línea
        dates_frame = ttk.Frame(details_frame)
        dates_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        dates_frame.columnconfigure(1, weight=1)
        dates_frame.columnconfigure(3, weight=1)

        ttk.Label(dates_frame, text="Inicio:", style='Title.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.start_date_entry = ttk.Entry(dates_frame, width=12, font=('Arial', 9))
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        self.start_date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ttk.Label(dates_frame, text="Fin:", style='Title.TLabel').grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        self.end_date_entry = ttk.Entry(dates_frame, width=12, font=('Arial', 9))
        self.end_date_entry.grid(row=0, column=3, sticky=tk.W)
        tomorrow = datetime.now() + timedelta(days=1)
        self.end_date_entry.insert(0, tomorrow.strftime("%d/%m/%Y"))

        # Servicios en una cuadrícula compacta
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
            row = i % 2  # 2 columnas
            col = i // 2 * 2  # 0, 0, 2, 2
            
            ttk.Label(services_frame, text=label, style='Title.TLabel').grid(
                row=row, column=col, sticky=tk.W, pady=2, padx=(0, 5))
            
            var = tk.IntVar(value=0)
            spinbox = ttk.Spinbox(services_frame, 
                                from_=0, 
                                to=100, 
                                textvariable=var, 
                                width=8, 
                                font=('Arial', 9))
            spinbox.grid(row=row, column=col+1, sticky=tk.W, pady=2, padx=(0, 15))
            self.service_vars[name] = var

        # Sección: Método de pago - COMPACTO
        payment_frame = ttk.LabelFrame(main_frame, 
                                    text="Método de Pago", 
                                    padding=10)
        payment_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Método de pago en una línea CON LA TARJETA AL LADO
        method_frame = ttk.Frame(payment_frame)
        method_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        method_frame.columnconfigure(3, weight=1)  # Para que el combobox se expanda

        ttk.Label(method_frame, text="Método:", style='Title.TLabel').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.payment_method_var = tk.StringVar(value="CASH")
        cash_rb = ttk.Radiobutton(method_frame, 
                                text="Efectivo", 
                                variable=self.payment_method_var, 
                                value="CASH", 
                                command=self._on_payment_method_change)
        cash_rb.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))

        card_rb = ttk.Radiobutton(method_frame, 
                                text="Tarjeta", 
                                variable=self.payment_method_var, 
                                value="CARD", 
                                command=self._on_payment_method_change)
        card_rb.grid(row=0, column=2, sticky=tk.W, padx=(0, 15))

        # Selección de tarjeta AL LADO de los radio buttons
        self.card_combo = ttk.Combobox(method_frame, 
                                    values=[f"{card.card_number} - {card.card_pin}" for card in self.cards], 
                                    state="disabled", 
                                    font=('Arial', 9),
                                    width=20)
        self.card_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(10, 0))

        if self.cards:
            self.card_combo.set(self.cards[0].card_number)

        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        
        self.submit_btn = ttk.Button(button_frame, 
                                   text="Crear Dieta", 
                                   command=self._on_submit)
        self.submit_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(button_frame, 
                              text="Cancelar", 
                              command=self._on_cancel)
        cancel_btn.pack(side=tk.RIGHT)


        # Estado inicial
        self._on_diet_type_change()
        self._on_payment_method_change()

    def _on_diet_type_change(self):
        """Maneja el cambio entre dieta individual y grupal sin mover elementos"""
        if self.diet_type_var.get() == "INDIVIDUAL":
            self.individual_frame.grid()
            self.multi_selection_frame.grid_remove()
        else:
            self.individual_frame.grid_remove()
            self.multi_selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def _add_selected_user(self):
        """Agrega usuario seleccionado a la lista de seleccionados"""
        selection = self.available_users_listbox.curselection()
        if selection:
            user_text = self.available_users_listbox.get(selection[0])
            self.available_users_listbox.delete(selection[0])
            self.selected_users_listbox.insert(tk.END, user_text)

    def _remove_selected_user(self):
        """Remueve usuario seleccionado de la lista de seleccionados"""
        selection = self.selected_users_listbox.curselection()
        if selection:
            user_text = self.selected_users_listbox.get(selection[0])
            self.selected_users_listbox.delete(selection[0])
            self.available_users_listbox.insert(tk.END, user_text)

    def _on_payment_method_change(self):
        """Habilita/deshabilita la selección de tarjeta según el método de pago"""
        if self.payment_method_var.get() == "CARD":
            self.card_combo.config(state="readonly")
        else:
            self.card_combo.config(state="disabled")

    def _load_diet_data(self):
        """Carga los datos de la dieta existente para edición"""
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
        
        self.submit_btn.config(text="Actualizar Dieta")

    def _on_submit(self):
        """Maneja el envío del formulario"""
        data = self.get_data()
        print(data)
        if self.is_edit_mode:
            dto_convert = DietUpdateDTO(
                start_date = data['start_date'],
                end_date = data['end_date'],
                description = data['description'],
                breakfast_count = data['breakfast_count'],
                lunch_count = data['lunch_count'],
                dinner_count = data['dinner_count'],
                accommodation_count = data['accommodation_count'],
                accommodation_payment_method = data['accommodation_payment_method'],
                accommodation_card_id = data['accommodation_card_id']
            )
            self.diet_service.update_diet(self.current_diet_id, dto_convert)
        else:
            
            id = self.diet_service.get_diet_service_by_local(data['is_local'])
            diet_create = DietCreateDTO(
                start_date = data['start_date'],
                end_date = data['end_date'],
                is_local = data['is_local'], 
                is_group = data['is_group'],
                description = data['description'],
                request_user_id = data['user_ids'],
                diet_service_id = id.id,
                breakfast_count = data['breakfast_count'],
                lunch_count = data['lunch_count'],
                dinner_count = data['dinner_count'],
                accommodation_count = data['accommodation_count'],
                accommodation_payment_method = data['accommodation_payment_method'],
                accommodation_card_id = data['accommodation_card_id']
            )
            self.diet_service.create_diet(diet_create)
            

    def _on_cancel(self):
        """Maneja la cancelación"""
        self.master.destroy() if hasattr(self.master, 'destroy') else self.clear()

    def get_data(self):
        """Obtiene los datos del formulario"""
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

    def clear(self):
        """Limpia el formulario"""
        self.description_entry.delete(0, tk.END)
        self.is_local_var.set(True)
        self.diet_type_var.set("INDIVIDUAL")
        self._on_diet_type_change()
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.end_date_entry.delete(0, tk.END)
        tomorrow = datetime.now() + timedelta(days=1)
        self.end_date_entry.insert(0, tomorrow.strftime("%d/%m/%Y"))
        
        for var in self.service_vars.values():
            var.set(0)
        
        self.payment_method_var.set("CASH")
        self._on_payment_method_change()
        
        self.user_combo.set('')
        self.available_users_listbox.delete(0, tk.END)
        self.selected_users_listbox.delete(0, tk.END)
        for user in self.users:
            self.available_users_listbox.insert(tk.END, f"{user.fullname} ({user.ci})")
        
        self.card_combo.set(self.cards[0].card_number if self.cards else '')
        
        self.is_edit_mode = False
        self.current_diet_id = None
        self.submit_btn.config(text="Crear Dieta")