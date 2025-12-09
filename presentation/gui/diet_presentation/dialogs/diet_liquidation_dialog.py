import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from application.dtos.diet_dtos import DietLiquidationCreateDTO
from application.services.card_service import CardService
from application.services.diet_service import DietAppService
from core.entities import diet_service

class DietLiquidationDialog(tk.Toplevel):
    """
    Diálogo para liquidar una dieta
    """
    
    def __init__(self, parent, diet_controller, diet, card_service: CardService, diet_service: DietAppService):
        super().__init__(parent)
        self.diet_controller = diet_controller
        self.diet = diet
        self.result = False
        self.card_service = card_service
        self.diet_service = diet_service

        self.title(f"Liquidar Dieta #{diet.advance_number}")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
    
    def calculate_total(self, breakfast_count, lunch_count, dinner_count, accommodation_count):
        """Calcula el total basado en los precios del servicio"""
        try:
            if not self.diet_controller:
                return 0.0
            
            # Obtener el servicio de dieta según si es local o no
            service = self.diet_controller.get_diet_service_by_local(self.diet.is_local)
            
            if not service:
                return 0.0
            
            # Calcular total
            breakfast_total = breakfast_count * service.breakfast_price
            lunch_total = lunch_count * service.lunch_price
            dinner_total = dinner_count * service.dinner_price
            
            # Usar precio correcto según método de pago
            if self.diet.accommodation_payment_method == "CARD":
                accommodation_total = accommodation_count * service.accommodation_card_price
            else:
                accommodation_total = accommodation_count * service.accommodation_cash_price
            
            total = breakfast_total + lunch_total + dinner_total + accommodation_total            
            return total
            
        except Exception as e:
            print(f"ERROR calculando total: {e}")
            return 0.0
    
    def update_total(self, *args):
        """Actualiza el monto total cuando cambian las cantidades"""
        try:
            # Obtener valores actuales de los Spinbox
            breakfast_count = self.liquidation_vars["desayunos"].get()
            lunch_count = self.liquidation_vars["almuerzos"].get()
            dinner_count = self.liquidation_vars["comidas"].get()
            accommodation_count = self.liquidation_vars["alojamientos"].get()
            
            # Calcular nuevo total
            new_total = self.calculate_total(
                breakfast_count,
                lunch_count,
                dinner_count,
                accommodation_count
            )
            
            # Actualizar el label
            self.total_var.set(f"Monto total a liquidar: ${new_total:.2f}")
            
        except Exception as e:
            print(f"Error actualizando total: {e}")
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del anticipo
        info_frame = ttk.LabelFrame(main_frame, text="Información del Anticipo", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Descripción: {self.diet.description}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Fechas: {self.diet.start_date} a {self.diet.end_date}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Método pago alojamiento: {self.diet.accommodation_payment_method}").pack(anchor=tk.W)
        
        # Calcular monto total inicial
        initial_total = self.calculate_total(
            self.diet.breakfast_count,
            self.diet.lunch_count,
            self.diet.dinner_count,
            self.diet.accommodation_count
        )
        
        # Variable para el monto total (se actualizará dinámicamente)
        self.total_var = tk.StringVar(value=f"Monto total a liquidar: ${initial_total:.2f}")
        total_label = ttk.Label(info_frame, textvariable=self.total_var, font=('Arial', 10, 'bold'))
        total_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Servicios a liquidar
        services_frame = ttk.LabelFrame(main_frame, text="Servicios a Liquidar", padding=10)
        services_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Variables para los Spinbox
        self.liquidation_vars = {
            "desayunos": tk.IntVar(value=self.diet.breakfast_count),
            "almuerzos": tk.IntVar(value=self.diet.lunch_count),
            "comidas": tk.IntVar(value=self.diet.dinner_count),
            "alojamientos": tk.IntVar(value=self.diet.accommodation_count)
        }
        
        # Configurar el trace para cada variable (para actualizar el total automáticamente)
        for var in self.liquidation_vars.values():
            var.trace_add("write", self.update_total)
        
        # Frame para editar cantidades
        edit_frame = ttk.Frame(services_frame)
        edit_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Desayunos
        ttk.Label(edit_frame, text="Desayunos:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        breakfast_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.breakfast_count, 
                                   textvariable=self.liquidation_vars["desayunos"], width=10,
                                   command=self.update_total)
        breakfast_spin.grid(row=0, column=1, padx=(0, 15), pady=5)
        
        # Almuerzos
        ttk.Label(edit_frame, text="Almuerzos:").grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.W)
        lunch_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.lunch_count,
                               textvariable=self.liquidation_vars["almuerzos"], width=10,
                               command=self.update_total)
        lunch_spin.grid(row=0, column=3, padx=(0, 15), pady=5)
        
        # Comidas
        ttk.Label(edit_frame, text="Comidas:").grid(row=1, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        dinner_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.dinner_count,
                                textvariable=self.liquidation_vars["comidas"], width=10,
                                command=self.update_total)
        dinner_spin.grid(row=1, column=1, padx=(0, 15), pady=5)
        
        # Alojamientos
        ttk.Label(edit_frame, text="Alojamientos:").grid(row=1, column=2, padx=(0, 5), pady=5, sticky=tk.W)
        accommodation_spin = ttk.Spinbox(edit_frame, from_=0, to=self.diet.accommodation_count,
                                       textvariable=self.liquidation_vars["alojamientos"], width=10,
                                       command=self.update_total)
        accommodation_spin.grid(row=1, column=3, padx=(0, 15), pady=5)
        
        # Información de límites
        limits_frame = ttk.Frame(services_frame)
        limits_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(limits_frame, text=f"Límites: Desayunos({self.diet.breakfast_count}), "
                                   f"Almuerzos({self.diet.lunch_count}), "
                                   f"Comidas({self.diet.dinner_count}), "
                                   f"Alojamientos({self.diet.accommodation_count})",
                font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Liquidar", command=self.on_liquidate).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)
    
    def center_on_parent(self, parent):
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def on_liquidate(self):
        try:
            # Validar que no se excedan las cantidades solicitadas
            if (self.liquidation_vars["desayunos"].get() > self.diet.breakfast_count or
                self.liquidation_vars["almuerzos"].get() > self.diet.lunch_count or
                self.liquidation_vars["comidas"].get() > self.diet.dinner_count or
                self.liquidation_vars["alojamientos"].get() > self.diet.accommodation_count):
                messagebox.showwarning("Validación", "Las cantidades liquidadas no pueden exceder las solicitadas")
                return
            
            create_dto = DietLiquidationCreateDTO(
                diet_id=self.diet.id,
                liquidation_date=datetime.now(),
                breakfast_count_liquidated=self.liquidation_vars["desayunos"].get(),
                lunch_count_liquidated=self.liquidation_vars["almuerzos"].get(),
                dinner_count_liquidated=self.liquidation_vars["comidas"].get(),
                accommodation_count_liquidated=self.liquidation_vars["alojamientos"].get(),
                accommodation_payment_method=self.diet.accommodation_payment_method,
                diet_service_id=self.diet.diet_service_id,
                accommodation_card_id=self.diet.accommodation_card_id
            )
           
            
            result = self.diet_controller.create_diet_liquidation(create_dto)
            if result:
                self.result = True
                messagebox.showinfo("Éxito", "Dieta liquidada correctamente")
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo liquidar la dieta")
            

            if self.diet.accommodation_payment_method.upper() == 'CARD':
                price = self.diet_service.get_diet_service_by_id(create_dto.diet_service_id).accommodation_card_price 
                self.card_service.discount_card(self.diet.accommodation_card_id, self.liquidation_vars["alojamientos"].get() * price)
            
            if not self.diet_service.card_on_the_road(self.diet.accommodation_card_id):
                self.card_service.toggle_card_active(self.diet.accommodation_card_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al liquidar: {str(e)}")
            import traceback
            traceback.print_exc()
            
            
          
