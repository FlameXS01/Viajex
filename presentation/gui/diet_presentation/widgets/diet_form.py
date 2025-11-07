import tkinter as tk
from tkinter import ttk
from datetime import datetime
from application.dtos.diet_dtos import DietCreateDTO, DietUpdateDTO

class DietForm(ttk.Frame):
    """
    Formulario para crear/editar dietas
    """
    
    def __init__(self, parent, diet_controller, diet=None):
        super().__init__(parent)
        self.diet_controller = diet_controller
        self.diet = diet
        
        self.create_widgets()
        if diet:
            self.load_diet_data()
    
    def create_widgets(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Información básica
        basic_frame = ttk.LabelFrame(main_frame, text="Información Básica", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(basic_frame, text="Descripción:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.description_entry = ttk.Entry(basic_frame, width=40)
        self.description_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(5, 0))
        
        ttk.Label(basic_frame, text="Local:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.is_local_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(basic_frame, variable=self.is_local_var).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="Grupal:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.is_group_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_frame, variable=self.is_group_var).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Fechas
        dates_frame = ttk.LabelFrame(main_frame, text="Fechas", padding=10)
        dates_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dates_frame, text="Fecha Inicio:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date_entry = ttk.Entry(dates_frame)
        self.start_date_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(5, 0))
        
        ttk.Label(dates_frame, text="Fecha Fin:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_date_entry = ttk.Entry(dates_frame)
        self.end_date_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(5, 0))
        
        # Servicios solicitados
        services_frame = ttk.LabelFrame(main_frame, text="Servicios Solicitados", padding=10)
        services_frame.pack(fill=tk.X, pady=(0, 10))
        
        services = [
            ("Desayunos:", "breakfast_count"),
            ("Almuerzos:", "lunch_count"), 
            ("Comidas:", "dinner_count"),
            ("Alojamientos:", "accommodation_count")
        ]
        
        self.service_vars = {}
        for i, (label, name) in enumerate(services):
            ttk.Label(services_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.IntVar(value=0)
            spinbox = ttk.Spinbox(services_frame, from_=0, to=100, textvariable=var, width=10)
            spinbox.grid(row=i, column=1, sticky=tk.W, pady=5, padx=(5, 0))
            self.service_vars[name] = var
        
        # Método de pago alojamiento
        payment_frame = ttk.LabelFrame(main_frame, text="Pago de Alojamiento", padding=10)
        payment_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.payment_method_var = tk.StringVar(value="CASH")
        ttk.Radiobutton(payment_frame, text="Efectivo", 
                       variable=self.payment_method_var, value="CASH").pack(anchor=tk.W)
        ttk.Radiobutton(payment_frame, text="Tarjeta", 
                       variable=self.payment_method_var, value="CARD").pack(anchor=tk.W)
        
        ttk.Label(payment_frame, text="Tarjeta:").pack(anchor=tk.W, pady=(10, 5))
        self.card_combo = ttk.Combobox(payment_frame, state="readonly")
        self.card_combo.pack(fill=tk.X, pady=(0, 5))
        
        # Configurar columnas
        for frame in [basic_frame, dates_frame, services_frame]:
            frame.columnconfigure(1, weight=1)
    
    def load_diet_data(self):
        """Carga los datos de la dieta en el formulario"""
        if not self.diet:
            return
            
        self.description_entry.insert(0, self.diet.description)
        self.is_local_var.set(self.diet.is_local)
        self.is_group_var.set(self.diet.is_group)
        self.start_date_entry.insert(0, self.diet.start_date.strftime("%d/%m/%Y"))
        self.end_date_entry.insert(0, self.diet.end_date.strftime("%d/%m/%Y"))
        
        self.service_vars["breakfast_count"].set(self.diet.breakfast_count)
        self.service_vars["lunch_count"].set(self.diet.lunch_count)
        self.service_vars["dinner_count"].set(self.diet.dinner_count)
        self.service_vars["accommodation_count"].set(self.diet.accommodation_count)
        
        self.payment_method_var.set(self.diet.accommodation_payment_method)
    
    def get_form_data(self) -> dict:
        """Obtiene los datos del formulario"""
        return {
            "description": self.description_entry.get(),
            "is_local": self.is_local_var.get(),
            "is_group": self.is_group_var.get(),
            "start_date": self.start_date_entry.get(),
            "end_date": self.end_date_entry.get(),
            "breakfast_count": self.service_vars["breakfast_count"].get(),
            "lunch_count": self.service_vars["lunch_count"].get(),
            "dinner_count": self.service_vars["dinner_count"].get(),
            "accommodation_count": self.service_vars["accommodation_count"].get(),
            "accommodation_payment_method": self.payment_method_var.get(),
            "accommodation_card_id": None  # Se asignará después
        }