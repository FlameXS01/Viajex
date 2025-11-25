import tkinter as tk
from tkinter import ttk
from datetime import datetime
from application.dtos.diet_dtos import DietLiquidationResponseDTO
from application.services.diet_service import DietAppService

class LiquidationInfoDialog(tk.Toplevel):
    """Diálogo para mostrar información de liquidación en modo de solo lectura"""
    
    def __init__(self, parent, diet_service: DietAppService, request_user_service, card_service, liquidation: DietLiquidationResponseDTO):
        super().__init__(parent)
        self.diet_service = diet_service
        self.liquidation = liquidation
        self.request_user_service = request_user_service
        self.card_service = card_service
        
        self.title(f"Información de Liquidación #{liquidation.liquidation_number}")
        self.geometry("800x650")
        self.minsize(800, 650)
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, 
                               text=f"Información de Liquidación #{self.liquidation.liquidation_number}",
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        info_frame = ttk.LabelFrame(main_frame, text="Datos Generales", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_info_rows(info_frame)
        
        services_frame = ttk.LabelFrame(main_frame, text="Servicios Liquidados", padding=15)
        services_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_services_with_prices(services_frame)
        
        status_frame = ttk.LabelFrame(main_frame, text="Información Adicional", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_additional_info(status_frame)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cerrar", command=self.destroy).pack(side=tk.RIGHT)
    
    def create_info_rows(self, parent):
        # Obtener información de la dieta asociada
        diet = self.diet_service.get_diet(self.liquidation.diet_id)
        user = self.request_user_service.get_user_by_id(diet.request_user_id) if diet else None
        solicitante = f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A"
        
        info_data = [
            ("N° Liquidación:", self.liquidation.liquidation_number),
            ("N° Anticipo:", diet.advance_number if diet else "N/A"),
            ("Solicitante:", solicitante),
            ("Fecha Liquidación:", self.liquidation.liquidation_date.strftime("%d/%m/%Y") if self.liquidation.liquidation_date else "N/A"),
            ("Localidad:", "Local" if diet.is_local else "Foráneo") if diet else ("Localidad:", "N/A")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=("Arial", 9)).pack(side=tk.LEFT, padx=(10, 0))
    
    def create_services_with_prices(self, parent):
        try:
            diet = self.diet_service.get_diet(self.liquidation.diet_id)
            service = self.diet_service.get_diet_service_by_local(diet.is_local) if diet else None
            
            if not service:
                ttk.Label(parent, text="No hay información de precios disponible", font=("Arial", 9)).pack(anchor=tk.W)
                return

            # Encabezados de la tabla
            headers_frame = ttk.Frame(parent)
            headers_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(headers_frame, text="Servicio", font=("Arial", 9, "bold"), width=12, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(headers_frame, text="Cant. Liq.", font=("Arial", 9, "bold"), width=10, anchor=tk.CENTER).pack(side=tk.LEFT)
            ttk.Label(headers_frame, text="Precio Unit.", font=("Arial", 9, "bold"), width=12, anchor=tk.CENTER).pack(side=tk.LEFT)
            ttk.Label(headers_frame, text="Subtotal", font=("Arial", 9, "bold"), width=12, anchor=tk.CENTER).pack(side=tk.LEFT)

            services_data = [
                ("Desayunos", self.liquidation.breakfast_count_liquidated, service.breakfast_price),
                ("Almuerzos", self.liquidation.lunch_count_liquidated, service.lunch_price),
                ("Cenas", self.liquidation.dinner_count_liquidated, service.dinner_price)
            ]

            # Precio de alojamiento según método de pago
            if diet.accommodation_payment_method == "CARD":
                accommodation_price = service.accommodation_card_price
            else:
                accommodation_price = service.accommodation_cash_price
            
            services_data.append(("Alojamientos", self.liquidation.accommodation_count_liquidated, accommodation_price))

            total_general = 0
            for service_name, count, unit_price in services_data:
                row_frame = ttk.Frame(parent)
                row_frame.pack(fill=tk.X, pady=3)
                
                ttk.Label(row_frame, text=service_name, font=("Arial", 9), width=12, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=str(count), font=("Arial", 9), width=10, anchor=tk.CENTER).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"${unit_price:.2f}", font=("Arial", 9), width=12, anchor=tk.CENTER).pack(side=tk.LEFT)
                
                subtotal = count * unit_price
                total_general += subtotal
                ttk.Label(row_frame, text=f"${subtotal:.2f}", font=("Arial", 9), width=12, anchor=tk.CENTER).pack(side=tk.LEFT)

            # Línea separadora
            separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
            separator.pack(fill=tk.X, pady=10)

            # Total general
            total_frame = ttk.Frame(parent)
            total_frame.pack(fill=tk.X)
            
            ttk.Label(total_frame, text="TOTAL LIQUIDADO:", font=("Arial", 10, "bold"), width=12, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(total_frame, text="", width=10, anchor=tk.CENTER).pack(side=tk.LEFT)
            ttk.Label(total_frame, text="", width=12, anchor=tk.CENTER).pack(side=tk.LEFT)
            ttk.Label(total_frame, text=f"${total_general:.2f}", font=("Arial", 10, "bold"), width=12, anchor=tk.CENTER).pack(side=tk.LEFT)

        except Exception as e:
            ttk.Label(parent, text=f"Error al cargar servicios: {str(e)}", font=("Arial", 9)).pack(anchor=tk.W)
    
    def create_additional_info(self, parent):
        diet = self.diet_service.get_diet(self.liquidation.diet_id)
        
        info_data = [
            ("Estado:", "✅ Liquidada"),
            ("Anticipo Asociado:", f"#{diet.advance_number}" if diet else "N/A"),
            ("Método Pago Aloj:", "Efectivo" if diet and diet.accommodation_payment_method == "CASH" else "Tarjeta")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=18, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=("Arial", 9)).pack(side=tk.LEFT, padx=(10, 0))
    
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