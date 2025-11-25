import tkinter as tk
from tkinter import ttk
from datetime import datetime
from application.dtos.diet_dtos import DietResponseDTO
from application.services.diet_service import DietAppService

class DietInfoDialog(tk.Toplevel):
    """Diálogo para mostrar información de dieta en modo de solo lectura"""
    
    def __init__(self, parent, diet_service: DietAppService, request_user_service, card_service, diet: DietResponseDTO):
        super().__init__(parent)
        self.diet_service = diet_service
        self.diet = diet
        self.request_user_service = request_user_service
        self.card_service = card_service
        
        self.title(f"Información de Dieta #{diet.advance_number}")
        self.geometry("700x600")
        self.minsize(700, 600)
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, 
                               text=f"Información Detallada - Dieta #{self.diet.advance_number}",
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        info_frame = ttk.LabelFrame(main_frame, text="Datos Generales", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_info_rows(info_frame)
        
        services_frame = ttk.LabelFrame(main_frame, text="Servicios Solicitados", padding=15)
        services_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_services_rows(services_frame)
        
        prices_frame = ttk.LabelFrame(main_frame, text="Información de Precios", padding=15)
        prices_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_prices_info(prices_frame)
        
        status_frame = ttk.LabelFrame(main_frame, text="Estado", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_status_info(status_frame)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cerrar", command=self.destroy).pack(side=tk.RIGHT)
    
    def create_info_rows(self, parent):
        user = self.request_user_service.get_user_by_id(self.diet.request_user_id)
        solicitante = f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A"
        
        info_data = [
            ("N° Anticipo:", self.diet.advance_number),
            ("Solicitante:", solicitante),
            ("Descripción:", self.diet.description),
            ("Fecha Inicio:", self.diet.start_date.strftime("%d/%m/%Y") if self.diet.start_date else "N/A"),
            ("Fecha Fin:", self.diet.end_date.strftime("%d/%m/%Y") if self.diet.end_date else "N/A"),
            ("Tipo:", "Grupal" if self.diet.is_group else "Individual"),
            ("Localidad:", "Local" if self.diet.is_local else "Foráneo")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=("Arial", 9)).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_services_rows(self, parent):
        services_data = [
            ("Desayunos:", self.diet.breakfast_count),
            ("Almuerzos:", self.diet.lunch_count),
            ("Cenas:", self.diet.dinner_count),
            ("Alojamientos:", self.diet.accommodation_count)
        ]
        
        for i, (label, value) in enumerate(services_data):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=("Arial", 9)).pack(side=tk.LEFT, padx=(10, 0))
        
        metodo_pago = "Efectivo" if self.diet.accommodation_payment_method == "CASH" else "Tarjeta"
        pago_frame = ttk.Frame(parent)
        pago_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(pago_frame, text="Método Pago Aloj:", font=("Arial", 9, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(pago_frame, text=metodo_pago, font=("Arial", 9)).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_prices_info(self, parent):
        try:
            service = self.diet_service.get_diet_service_by_local(self.diet.is_local)
            if service:
                prices_data = [
                    ("Precio Desayuno:", f"${service.breakfast_price:.2f}"),
                    ("Precio Almuerzo:", f"${service.lunch_price:.2f}"),
                    ("Precio Cena:", f"${service.dinner_price:.2f}"),
                    ("Precio Alojamiento:", f"${service.accommodation_cash_price:.2f} (Efectivo)")
                ]
                
                for i, (label, value) in enumerate(prices_data):
                    row_frame = ttk.Frame(parent)
                    row_frame.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=20, anchor=tk.W).pack(side=tk.LEFT)
                    ttk.Label(row_frame, text=str(value), font=("Arial", 9)).pack(side=tk.LEFT, padx=(10, 0))
                
                total = self.calculate_total()
                total_frame = ttk.Frame(parent)
                total_frame.pack(fill=tk.X, pady=(10, 0))
                
                ttk.Label(total_frame, text="TOTAL ESTIMADO:", font=("Arial", 10, "bold"), anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(total_frame, text=f"${total:.2f}", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(10, 0))
            else:
                ttk.Label(parent, text="No hay información de precios disponible", font=("Arial", 9)).pack(anchor=tk.W)
        except Exception as e:
            ttk.Label(parent, text=f"Error al cargar precios: {str(e)}", font=("Arial", 9)).pack(anchor=tk.W)
    
    def create_status_info(self, parent):
        status_map = {
            "requested": "🟡 Solicitada",
            "liquidated": "🔵 Liquidada"
        }
        
        status_display = status_map.get(self.diet.status, self.diet.status)
        
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(status_frame, text="Estado:", font=("Arial", 10, "bold"), width=10, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(status_frame, text=status_display, font=("Arial", 10)).pack(side=tk.LEFT, padx=(10, 0))
        
    
    def calculate_total(self):
        try:
            service = self.diet_service.get_diet_service_by_local(self.diet.is_local)
            if not service:
                return 0.0
            
            breakfast_total = self.diet.breakfast_count * service.breakfast_price
            lunch_total = self.diet.lunch_count * service.lunch_price
            dinner_total = self.diet.dinner_count * service.dinner_price
            
            if self.diet.accommodation_payment_method == "CARD":
                accommodation_total = self.diet.accommodation_count * service.accommodation_card_price
            else:
                accommodation_total = self.diet.accommodation_count * service.accommodation_cash_price
            
            return breakfast_total + lunch_total + dinner_total + accommodation_total
        except Exception as e:
            print(f"Error calculando total: {e}")
            return 0.0
    
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