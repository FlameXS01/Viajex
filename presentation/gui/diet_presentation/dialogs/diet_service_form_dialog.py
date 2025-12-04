import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from application.dtos.diet_dtos import DietServiceResponseDTO
from application.services.diet_service import DietAppService

class DietServiceFormDialog(tk.Toplevel):
    """Diálogo para agregar/editar servicios de dieta"""
    
    def __init__(self, parent, diet_service: DietAppService, service: Optional[DietServiceResponseDTO] = None):
        super().__init__(parent)
        self.diet_service = diet_service
        self.service = service
        self.result = False
        
        self._setup_dialog()
        self._create_widgets()
        if self.service:
            self._load_data()
        
    def _setup_dialog(self):
        """Configura el diálogo"""
        title = "Editar Servicio" if self.service else "Agregar Servicio"
        self.title(title)
        self.geometry("400x450")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        
        # Centrar en la pantalla
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Crea los widgets del formulario"""
        # Frame principal
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_text = "Editar Servicio de Dieta" if self.service else "Agregar Servicio de Dieta"
        title_label = ttk.Label(main_frame, text=title_text, 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame del formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tipo de servicio
        ttk.Label(form_frame, text="Tipo de Servicio:").grid(row=0, column=0, sticky="w", pady=5)
        self.service_type_var = tk.BooleanVar(value=True)  # True = Local, False = Fuera
        service_frame = ttk.Frame(form_frame)
        service_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Radiobutton(service_frame, text="Local", variable=self.service_type_var, 
                       value=True).pack(side=tk.LEFT)
        ttk.Radiobutton(service_frame, text="Fuera de provincia", variable=self.service_type_var, 
                       value=False).pack(side=tk.LEFT, padx=(20, 0))
        
        # Precio Desayuno
        ttk.Label(form_frame, text="Precio Desayuno ($):").grid(row=1, column=0, sticky="w", pady=5)
        self.breakfast_var = tk.StringVar()
        breakfast_entry = ttk.Entry(form_frame, textvariable=self.breakfast_var, width=15)
        breakfast_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Precio Almuerzo
        ttk.Label(form_frame, text="Precio Almuerzo ($):").grid(row=2, column=0, sticky="w", pady=5)
        self.lunch_var = tk.StringVar()
        lunch_entry = ttk.Entry(form_frame, textvariable=self.lunch_var, width=15)
        lunch_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Precio Comida
        ttk.Label(form_frame, text="Precio Comida ($):").grid(row=3, column=0, sticky="w", pady=5)
        self.dinner_var = tk.StringVar()
        dinner_entry = ttk.Entry(form_frame, textvariable=self.dinner_var, width=15)
        dinner_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Precio Alojamiento Efectivo
        ttk.Label(form_frame, text="Alojamiento Efectivo ($):").grid(row=4, column=0, sticky="w", pady=5)
        self.accommodation_cash_var = tk.StringVar()
        accommodation_cash_entry = ttk.Entry(form_frame, textvariable=self.accommodation_cash_var, width=15)
        accommodation_cash_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # Precio Alojamiento Tarjeta
        ttk.Label(form_frame, text="Alojamiento Tarjeta ($):").grid(row=5, column=0, sticky="w", pady=5)
        self.accommodation_card_var = tk.StringVar()
        accommodation_card_entry = ttk.Entry(form_frame, textvariable=self.accommodation_card_var, width=15)
        accommodation_card_entry.grid(row=5, column=1, sticky="w", pady=5)
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Guardar", 
                  command=self._save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.destroy).pack(side=tk.RIGHT)
        
        # Configurar grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def _load_data(self):
        """Carga los datos del servicio en el formulario"""
        if not self.service:
            return
            
        self.service_type_var.set(self.service.is_local)
        self.breakfast_var.set(str(self.service.breakfast_price))
        self.lunch_var.set(str(self.service.lunch_price))
        self.dinner_var.set(str(self.service.dinner_price))
        self.accommodation_cash_var.set(str(self.service.accommodation_cash_price))
        self.accommodation_card_var.set(str(self.service.accommodation_card_price))
    
    def _save(self):
        """Guarda el servicio"""
        try:
            # Validar campos
            breakfast_price = self._validate_price(self.breakfast_var.get(), "Desayuno")
            lunch_price = self._validate_price(self.lunch_var.get(), "Almuerzo")
            dinner_price = self._validate_price(self.dinner_var.get(), "Comida")
            accommodation_cash_price = self._validate_price(self.accommodation_cash_var.get(), "Alojamiento Efectivo")
            accommodation_card_price = self._validate_price(self.accommodation_card_var.get(), "Alojamiento Tarjeta")
            
            if self.service:
                # Editar servicio existente
                success = self.diet_service.edit_diet_service(
                    service_id=self.service.id,
                    is_local=self.service_type_var.get(),
                    breakfast_price=breakfast_price,
                    lunch_price=lunch_price,
                    dinner_price=dinner_price,
                    accommodation_cash_price=accommodation_cash_price,
                    accommodation_card_price=accommodation_card_price
                )
            else:
                # Agregar nuevo servicio
                success = self.diet_service.add_diet_service(
                    is_local=self.service_type_var.get(),
                    breakfast_price=breakfast_price,
                    lunch_price=lunch_price,
                    dinner_price=dinner_price,
                    accommodation_cash_price=accommodation_cash_price,
                    accommodation_card_price=accommodation_card_price
                )
            if success:
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar el servicio")
                import traceback 
                traceback.print_exc()
                
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def _validate_price(self, price_str: str, field_name: str) -> float:
        """Valida que el precio sea un número válido"""
        if not price_str.strip():
            raise ValueError(f"El precio de {field_name} es requerido")
        
        try:
            price = float(price_str)
            if price < 0:
                raise ValueError(f"El precio de {field_name} no puede ser negativo")
            return price
        except ValueError:
            raise ValueError(f"El precio de {field_name} debe ser un número válido")