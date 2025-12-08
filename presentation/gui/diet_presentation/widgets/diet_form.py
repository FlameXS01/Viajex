import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkinter import messagebox
from typing import List, Optional, Dict, Any

from application.services.diet_service import DietAppService
from core.entities import diet_service


class DietForm(ttk.Frame):
    """
    
    Formulario para crear y editar dietas

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
        
        # Datos
        self.users = user_service.get_all_users() if user_service else []
        self.cards = card_service.get_all_cards() if card_service else []
        self.valid_cards = []
        
        # Variables de control
        self._setup_variables()
        
        # Configuración de la grilla principal
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._create_widgets()
        self._setup_bindings()
        
        if diet:
            self._load_diet_data()

    def _setup_variables(self):
        """Configura las variables de control del formulario"""
        # Información básica
        self.description_var = tk.StringVar()
        self.is_local_var = tk.BooleanVar(value=True)
        self.diet_type_var = tk.StringVar(value="GROUP")
        
        # Fechas
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        
        # Servicios
        self.service_vars = {
            "breakfast_count": tk.IntVar(value=0),
            "lunch_count": tk.IntVar(value=0),
            "dinner_count": tk.IntVar(value=0),
            "accommodation_count": tk.IntVar(value=0)
        }
        
        # Pago
        self.payment_method_var = tk.StringVar(value="CASH")
        self.selected_card_var = tk.StringVar()

    def _create_widgets(self):
        """Crea todos los widgets del formulario"""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Configurar filas para expansión
        for i in range(6):
            main_frame.rowconfigure(i, weight=0)
        main_frame.rowconfigure(5, weight=1)
        
        self._create_basic_info_section(main_frame)
        self._create_user_selection_section(main_frame)
        self._create_diet_details_section(main_frame)
        self._create_payment_section(main_frame)

        self.main_frame = main_frame

    def _create_basic_info_section(self, parent):
        """Crea la sección de información básica"""
        # Frame principal
        basic_info_frame = ttk.LabelFrame(
            parent, 
            text="📋 Información Básica", 
            padding=15
        )
        basic_info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        basic_info_frame.columnconfigure(1, weight=1)

        # Descripción
        ttk.Label(basic_info_frame, text="Descripción:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        
        self.description_entry = ttk.Entry(
            basic_info_frame, 
            textvariable=self.description_var,
            width=60,
            font=('Arial', 10)
        )
        self.description_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Tipo de dieta
        type_frame = ttk.Frame(basic_info_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(type_frame, text="Tipo de Dieta:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 20)
        )

        # Checkbutton para Local - BLOQUEADO EN MODO EDICIÓN
        self.local_check = ttk.Checkbutton(
            type_frame, 
            text="🏠 Local", 
            variable=self.is_local_var
        )
        self.local_check.grid(row=0, column=1, sticky=tk.W, padx=(0, 30))

        # Radio buttons para Individual/Grupal - BLOQUEADOS EN MODO EDICIÓN
        self.individual_radio = ttk.Radiobutton(
            type_frame, 
            text="👤 Individual", 
            variable=self.diet_type_var, 
            value="INDIVIDUAL", 
            command=self._on_diet_type_change
        )
        self.individual_radio.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))

        self.group_radio = ttk.Radiobutton(
            type_frame, 
            text="👥 Grupal", 
            variable=self.diet_type_var, 
            value="GROUP", 
            command=self._on_diet_type_change
        )
        self.group_radio.grid(row=0, column=3, sticky=tk.W)

        # BLOQUEAR CONTROLES EN MODO EDICIÓN
        if self.is_edit_mode:
            self.local_check.config(state='disabled')
            self.individual_radio.config(state='disabled')
            self.group_radio.config(state='disabled')

    def _create_user_selection_section(self, parent):
        """Crea la sección de selección de usuarios"""
        self.users_frame = ttk.LabelFrame(
            parent, 
            text="👥 Selección de Usuarios", 
            padding=15
        )
        self.users_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.users_frame.columnconfigure(0, weight=1)

        # CONTENEDOR PARA VISUALIZACIÓN EN MODO EDICIÓN
        self.view_only_container = ttk.Frame(self.users_frame)
        self.view_only_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.view_only_container.columnconfigure(0, weight=1)
        
        # Treeview para mostrar usuarios en modo edición (solo lectura)
        ttk.Label(self.view_only_container, text="Usuarios de la dieta:", 
                font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        columns = ("nombre", "ci")
        self.users_treeview = ttk.Treeview(
            self.view_only_container, 
            columns=columns, 
            show="headings", 
            height=6,
            selectmode="none"  # Deshabilitar selección
        )
        
        self.users_treeview.heading("nombre", text="Nombre Completo")
        self.users_treeview.heading("ci", text="Cédula")
        self.users_treeview.column("nombre", width=300)
        self.users_treeview.column("ci", width=150)
        
        self.users_treeview.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para el treeview
        tree_scrollbar = ttk.Scrollbar(
            self.view_only_container, 
            orient=tk.VERTICAL, 
            command=self.users_treeview.yview
        )
        tree_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.users_treeview.configure(yscrollcommand=tree_scrollbar.set)

        # Contenedor para los dos modos de selección (SOLO PARA CREACIÓN)
        self.selection_container = ttk.Frame(self.users_frame)
        self.selection_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.selection_container.columnconfigure(0, weight=1)

        # Modo Individual
        self.individual_frame = self._create_individual_selection()
        self.individual_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Modo Grupal
        self.group_frame = self._create_group_selection()
        self.group_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # MOSTRAR U OCULTAR SEGÚN MODO
        if self.is_edit_mode:
            self.selection_container.grid_remove()  # Ocultar selectores
            self.view_only_container.grid()         # Mostrar vista de solo lectura
        else:
            self.view_only_container.grid_remove()  # Ocultar vista de solo lectura
            self.selection_container.grid() 
            
    def _create_individual_selection(self):
        """Crea la interfaz para selección individual"""
        frame = ttk.Frame(self.selection_container)
        frame.columnconfigure(0, weight=1)
        
        ttk.Label(frame, text="Seleccionar Usuario:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 8)
        )
        
        user_values = [f"{user.fullname} ({user.ci})" for user in self.users]
        self.user_combo = ttk.Combobox(
            frame, 
            values=user_values, 
            state="readonly",
            textvariable=tk.StringVar(),
            height=8,
            font=('Arial', 10)
        )
        self.user_combo.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        if user_values:
            self.user_combo.set(user_values[0])
            
        return frame

    def _create_group_selection(self):
        """Crea la interfaz para selección grupal"""
        frame = ttk.Frame(self.selection_container)
        frame.columnconfigure(0, weight=1)
        
        # Frame para las listas y botones
        lists_frame = ttk.Frame(frame)
        lists_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        lists_frame.columnconfigure(0, weight=1)  # Lista disponibles
        lists_frame.columnconfigure(1, weight=0)  # Botones
        lists_frame.columnconfigure(2, weight=1)  # Lista seleccionados

        # Lista de usuarios disponibles
        ttk.Label(lists_frame, text="Usuarios Disponibles:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        available_frame = ttk.Frame(lists_frame)
        available_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        available_frame.columnconfigure(0, weight=1)
        available_frame.rowconfigure(0, weight=1)
        
        self.available_listbox = tk.Listbox(
            available_frame, 
            height=8, 
            selectmode=tk.SINGLE,
            font=('Arial', 9)
        )
        self.available_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        available_scrollbar = ttk.Scrollbar(
            available_frame, 
            orient=tk.VERTICAL, 
            command=self.available_listbox.yview
        )
        available_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.available_listbox.configure(yscrollcommand=available_scrollbar.set)

        # Botones de transferencia
        buttons_frame = ttk.Frame(lists_frame)
        buttons_frame.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=10)
        
        ttk.Button(
            buttons_frame, 
            text="➡️", 
            command=self._add_selected_user,
            width=4
        ).pack(pady=5)
        
        ttk.Button(
            buttons_frame, 
            text="⬅️", 
            command=self._remove_selected_user,
            width=4
        ).pack(pady=5)
        
        # Botones para selección masiva
        ttk.Button(
            buttons_frame, 
            text="⏩ Todos", 
            command=self._add_all_users,
            width=8
        ).pack(pady=5)
        
        ttk.Button(
            buttons_frame, 
            text="⏪ Todos", 
            command=self._remove_all_users,
            width=8
        ).pack(pady=5)

        # Lista de usuarios seleccionados
        ttk.Label(lists_frame, text="Usuarios Seleccionados:", font=('Arial', 9, 'bold')).grid(
            row=0, column=2, sticky=tk.W, pady=(0, 5)
        )
        
        selected_frame = ttk.Frame(lists_frame)
        selected_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        selected_frame.columnconfigure(0, weight=1)
        selected_frame.rowconfigure(0, weight=1)
        
        self.selected_listbox = tk.Listbox(
            selected_frame, 
            height=8, 
            selectmode=tk.SINGLE,
            font=('Arial', 9)
        )
        self.selected_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        selected_scrollbar = ttk.Scrollbar(
            selected_frame, 
            orient=tk.VERTICAL, 
            command=self.selected_listbox.yview
        )
        selected_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.selected_listbox.configure(yscrollcommand=selected_scrollbar.set)

        # Poblar lista de disponibles
        for user in self.users:
            self.available_listbox.insert(tk.END, f"{user.fullname} ({user.ci})")
            
        return frame

    def _create_diet_details_section(self, parent):
        """Crea la sección de detalles de la dieta"""
        details_frame = ttk.LabelFrame(
            parent, 
            text="📅 Detalles de la Dieta", 
            padding=15
        )
        details_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        details_frame.columnconfigure(1, weight=1)

        # Fechas
        dates_frame = ttk.Frame(details_frame)
        dates_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        dates_frame.columnconfigure(1, weight=1)
        dates_frame.columnconfigure(3, weight=1)

        ttk.Label(dates_frame, text="Fecha Inicio:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.start_date_entry = ttk.Entry(
            dates_frame, 
            textvariable=self.start_date_var,
            width=15,
            font=('Arial', 10)
        )
        self.start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 30))
        
        # Establecer fecha por defecto
        default_start = datetime.now().strftime("%d/%m/%Y")
        self.start_date_var.set(default_start)

        ttk.Label(dates_frame, text="Fecha Fin:", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 10)
        )
        
        self.end_date_entry = ttk.Entry(
            dates_frame, 
            textvariable=self.end_date_var,
            width=15,
            font=('Arial', 10)
        )
        self.end_date_entry.grid(row=0, column=3, sticky=tk.W)
        
        # Establecer fecha por defecto (mañana)
        default_end = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        self.end_date_var.set(default_end)

        # Servicios
        services_frame = ttk.Frame(details_frame)
        services_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        services_config = [
            ("🍳 Desayunos:", "breakfast_count"),
            ("🍲 Almuerzos:", "lunch_count"), 
            ("🍽️ Comidas:", "dinner_count"),
            ("🏨 Alojamientos:", "accommodation_count")
        ]
        
        for i, (label, var_name) in enumerate(services_config):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(services_frame, text=label, font=('Arial', 10)).grid(
                row=row, column=col, sticky=tk.W, pady=8, padx=(0, 10)
            )
            
            spinbox = ttk.Spinbox(
                services_frame, 
                from_=0, 
                to=999,
                textvariable=self.service_vars[var_name],
                width=8,
                font=('Arial', 10)
            )
            spinbox.grid(row=row, column=col + 1, sticky=tk.W, pady=8, padx=(0, 30))

    def _create_payment_section(self, parent):
        """Crea la sección de método de pago"""
        payment_frame = ttk.LabelFrame(
            parent, 
            text=" Método de Pago", 
            padding=15
        )
        payment_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        payment_frame.columnconfigure(1, weight=1)

        method_frame = ttk.Frame(payment_frame)
        method_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        method_frame.columnconfigure(1, weight=1)

        ttk.Label(method_frame, text="Método de Pago:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 15)
        )

        # Radio buttons para método de pago
        cash_radio = ttk.Radiobutton(
            method_frame, 
            text="💵 Efectivo", 
            variable=self.payment_method_var, 
            value="CASH", 
            command=self._on_payment_method_change
        )
        cash_radio.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        card_radio = ttk.Radiobutton(
            method_frame, 
            text="💳 Tarjeta", 
            variable=self.payment_method_var, 
            value="CARD", 
            command=self._on_payment_method_change
        )
        card_radio.grid(row=0, column=2, sticky=tk.W)

        # Combobox para tarjetas.
        
        self.valid_cards = [card for card in self.cards if card.balance > self.acumulative_price]
        card_values = [f"{card.card_number} - {card.card_pin}" for card in self.valid_cards]
        self.card_combo = ttk.Combobox(
            method_frame,
            values=card_values,
            textvariable=self.selected_card_var,
            state="readonly",
            width=25,
            font=('Arial', 10)
        )
        self.card_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(20, 0))

        if card_values:
            self.card_combo.set(card_values[0])

    def _setup_bindings(self):
        """Configura los enlaces de eventos"""
        # Validación básica de fechas
        self.start_date_entry.bind('<FocusOut>', self._validate_dates)
        self.end_date_entry.bind('<FocusOut>', self._validate_dates)
        self.service_vars["accommodation_count"].trace_add("write", self._on_accommodation_change)
        self.is_local_var.trace_add("write", self._on_accommodation_change)

    # ===== MÉTODOS DE MANEJO DE EVENTOS =====
    def _on_accommodation_change(self, *args):
        """Actualiza las tarjetas válidas cuando cambia la cantidad de hospedaje"""
        # Recalcular el precio acumulado
        data = self.get_form_data()  # Esto ya calcula self.acumulative_price
        
        # Actualizar la lista de tarjetas válidas
        if hasattr(self, 'card_combo') and self.payment_method_var.get() == "CARD":
            # Filtrar tarjetas con balance suficiente
            self.valid_cards = [card for card in self.cards if card.balance >= self.acumulative_price]
            card_values = [f"{card.card_number} - {card.card_pin}" for card in self.valid_cards]
            
            # Actualizar el combobox
            current_selection = self.selected_card_var.get()
            self.card_combo['values'] = card_values
            
            if card_values:
                # Mantener la selección anterior si sigue siendo válida
                if current_selection in card_values:
                    self.card_combo.set(current_selection)
                else:
                    self.card_combo.set(card_values[0])
            else:
                self.card_combo.set('')
                messagebox.showwarning(
                    "Tarjetas Insuficientes", 
                    f"No hay tarjetas con saldo suficiente (${self.acumulative_price:.2f} requeridos)"
                )

    def _on_diet_type_change(self):
        """Maneja el cambio entre modo individual y grupal"""
        if self.diet_type_var.get() == "INDIVIDUAL":
            self.individual_frame.grid()
            self.group_frame.grid_remove()
            self.user_combo.config(state="readonly")
            self._create_payment_section(self.main_frame)
        else:
            self.individual_frame.grid_remove()
            self.group_frame.grid()
            self._create_payment_section(self.main_frame)
            
        # Actualizar título de la sección
        new_title = "👤 Selección de Usuario" if self.diet_type_var.get() == "INDIVIDUAL" else "👥 Selección de Usuarios"
        self.users_frame.configure(text=new_title)

    def _on_payment_method_change(self):
        """Maneja el cambio de método de pago"""
        if self.payment_method_var.get() == "CARD":
            self.card_combo.config(state='readonly')
            self._on_accommodation_change()
        else:
            self.card_combo.config(state='disabled')

    def _add_selected_user(self):
        """Agrega usuario seleccionado a la lista de seleccionados"""
        selection = self.available_listbox.curselection()
        if selection:
            user_text = self.available_listbox.get(selection[0])
            self.available_listbox.delete(selection[0])
            self.selected_listbox.insert(tk.END, user_text)
            self._create_payment_section(self.main_frame)

    def _remove_selected_user(self):
        """Remueve usuario seleccionado de la lista de seleccionados"""
        selection = self.selected_listbox.curselection()
        if selection:
            user_text = self.selected_listbox.get(selection[0])
            self.selected_listbox.delete(selection[0])
            self.available_listbox.insert(tk.END, user_text)
            self._create_payment_section(self.main_frame)

    def _add_all_users(self):
        """Agrega todos los usuarios a la lista de seleccionados"""
        available_users = list(self.available_listbox.get(0, tk.END))
        for user in available_users:
            self.selected_listbox.insert(tk.END, user)
        self.available_listbox.delete(0, tk.END)

    def _remove_all_users(self):
        """Remueve todos los usuarios de la lista de seleccionados"""
        selected_users = list(self.selected_listbox.get(0, tk.END))
        for user in selected_users:
            self.available_listbox.insert(tk.END, user)
        self.selected_listbox.delete(0, tk.END)

    def _validate_dates(self, event=None):
        """Valida que las fechas tengan formato correcto"""
        # Implementación básica - puedes expandir esto
        try:
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            if start_date and end_date:
                datetime.strptime(start_date, "%d/%m/%Y")
                datetime.strptime(end_date, "%d/%m/%Y")
                
        except ValueError:
            
            pass

    # ===== MÉTODOS DE CARGA Y OBTENCIÓN DE DATOS =====

    def _load_diet_data(self):
        """Carga los datos de la dieta existente en el formulario"""
        if not self.diet:
            return
            
        # Información básica
        self.description_var.set(self.diet.description)
        self.is_local_var.set(self.diet.is_local)
        self.diet_type_var.set("GROUP" if self.diet.is_group else "INDIVIDUAL")
        
        # Fechas
        if self.diet.start_date:
            self.start_date_var.set(self.diet.start_date.strftime("%d/%m/%Y"))
        if self.diet.end_date:
            self.end_date_var.set(self.diet.end_date.strftime("%d/%m/%Y"))

        # Servicios
        self.service_vars["breakfast_count"].set(self.diet.breakfast_count)
        self.service_vars["lunch_count"].set(self.diet.lunch_count)
        self.service_vars["dinner_count"].set(self.diet.dinner_count)
        self.service_vars["accommodation_count"].set(self.diet.accommodation_count)
        
        # Pago
        self.payment_method_var.set(self.diet.accommodation_payment_method)
        self._on_payment_method_change()
        
        if self.diet.accommodation_card_id and self.cards:
            card = next((c for c in self.cards if c.id == self.diet.accommodation_card_id), None)
            if card:
                self.selected_card_var.set(f"{card.card_number} - {card.card_pin}")

        # Cargar usuarios 
        # diet_members = self.diet_member_service.list_diet_members(self.diet.id)
        user_ids = [self.diet.request_user_id]
        
        if self.is_edit_mode:
            # MODO EDICIÓN: Cargar en el Treeview de solo lectura
            for user_id in user_ids:
                user = next((u for u in self.users if u.id == user_id), None)
                if user:
                    self.users_treeview.insert("", "end", values=(user.fullname, user.ci))
            
            # Actualizar título según cantidad de usuarios
            user_count = len(user_ids)
            title_suffix = "Usuario" if user_count == 1 else "Usuarios"
            self.users_frame.configure(text=f"👥 {user_count} {title_suffix} de la Dieta")
            
        else:
            # MODO CREACIÓN: Cargar en los controles de selección normales
            if user_ids:
                if self.diet.is_group:
                    # Modo grupal
                    for user_id in user_ids:
                        user = next((u for u in self.users if u.id == user_id), None)
                        if user:
                            user_text = f"{user.fullname} ({user.ci})"
                            # Mover de disponibles a seleccionados
                            available_items = list(self.available_listbox.get(0, tk.END))
                            if user_text in available_items:
                                index = available_items.index(user_text)
                                self.available_listbox.delete(index)
                                self.selected_listbox.insert(tk.END, user_text)
                else:
                    # Modo individual
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

        # Actualizar la vista según el tipo de dieta (solo en modo creación)
        if not self.is_edit_mode:
            self._on_diet_type_change()

    def get_form_data(self):
        """
        Obtiene todos los datos del formulario en un diccionario
        """
        selected_user_ids = []
        total_request_user = 0
        if self.is_edit_mode:
            # EN MODO EDICIÓN: Usar el request_user_id de la dieta 
            selected_user_ids = [self.diet.request_user_id]
        else:
            # EN MODO CREACIÓN: Usar la selección normal
            if self.diet_type_var.get() == "INDIVIDUAL":
                # Modo individual
                selected_user = self.user_combo.get()
                if selected_user:
                    user = next((u for u in self.users if f"{u.fullname} ({u.ci})" == selected_user), None)
                    if user:
                        selected_user_ids = [user.id]
                total_request_user = 1
            else:
                # Modo grupal
                selected_count = self.selected_listbox.size()
                total_request_user = selected_count
                for i in range(selected_count):
                    user_text = self.selected_listbox.get(i)
                    user = next((u for u in self.users if f"{u.fullname} ({u.ci})" == user_text), None)
                    if user:
                        selected_user_ids.append(user.id)
                
        
        # El resto del código se mantiene igual...
        selected_card = self.selected_card_var.get()
        card_id = None
        if selected_card and self.payment_method_var.get() == "CARD":
            card = next((c for c in self.cards if f"{c.card_number} - {c.card_pin}" == selected_card), None)
            card_id = card.id if card else None
        
        total_acomodation_service = total_request_user * self.service_vars["accommodation_count"].get()
        if (self.is_local_var.get()):
            self.acumulative_price = total_acomodation_service * self.diet_service.get_diet_service_by_local(True).accommodation_card_price
        else:
            self.acumulative_price = total_acomodation_service * self.diet_service.get_diet_service_by_local(False).accommodation_card_price
        
        return {
            "description": self.description_var.get(),
            "is_local": self.is_local_var.get(),
            "is_group": self.diet_type_var.get() == "GROUP",
            "start_date": self.start_date_var.get(),
            "end_date": self.end_date_var.get(),
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
        
        # Validar descripción
        if not data["description"].strip():
            errors.append("La descripción es obligatoria")
            
        # Validar fechas
        try:
            start_date = datetime.strptime(data["start_date"], "%d/%m/%Y")
            end_date = datetime.strptime(data["end_date"], "%d/%m/%Y")
            
            if end_date < start_date:
                errors.append("La fecha de fin no puede ser anterior a la fecha de inicio")
                
        except ValueError:
            errors.append("Formato de fecha inválido. Use DD/MM/YYYY")
            
        # Validar usuarios seleccionados
        if not data["user_ids"]:
            errors.append("Debe seleccionar al menos un usuario")
            
        # Validar método de pago con tarjeta
        if data["accommodation_payment_method"] == "CARD" and not data["accommodation_card_id"]:
            errors.append("Debe seleccionar una tarjeta cuando el método de pago es tarjeta")
            
        return len(errors) == 0, errors