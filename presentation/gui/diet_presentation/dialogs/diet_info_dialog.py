import tkinter as tk
from tkinter import ttk
from datetime import datetime
from application.dtos.diet_dtos import DietResponseDTO
from application.services.diet_service import DietAppService

class DietInfoDialog(tk.Toplevel):
    """Diálogo para mostrar información de dieta en modo de solo lectura - OPTIMIZADO"""
    
    def __init__(self, parent, diet_service: DietAppService, request_user_service, card_service, diet: DietResponseDTO):
        super().__init__(parent)
        self.diet_service = diet_service
        self.diet = diet
        self.request_user_service = request_user_service
        self.card_service = card_service
        
        self.title(f"Información de Dieta #{diet.advance_number}")
        self.geometry("650x550")  # Reducido un poco
        self.minsize(650, 550)
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_on_parent(parent)
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, 
                               text=f"Información Detallada - Dieta #{self.diet.advance_number}",
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        info_frame = ttk.LabelFrame(main_frame, text="📋 Datos Generales", padding=12)
        info_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.create_info_rows(info_frame)
        
        # NUEVA SECCIÓN COMBINADA: Servicios + Precios
        services_prices_frame = ttk.LabelFrame(main_frame, text="💰 Servicios y Precios", padding=12)
        services_prices_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.create_services_with_prices(services_prices_frame)
        
        status_frame = ttk.LabelFrame(main_frame, text="📊 Estado ", padding=12)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_status_and_total(status_frame)
        
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
            ("Fechas:", f"{self.diet.start_date.strftime('%d/%m/%Y') if self.diet.start_date else 'N/A'} - {self.diet.end_date.strftime('%d/%m/%Y') if self.diet.end_date else 'N/A'}"),
            ("Tipo:", "👥 Grupal" if self.diet.is_group else "👤 Individual"),
            ("Localidad:", "🏠 Local" if self.diet.is_local else "🌍 Foráneo")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=12, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=("Arial", 9)).pack(side=tk.LEFT, padx=(8, 0))
    
    def create_services_with_prices(self, parent):
        try:
            service = self.diet_service.get_diet_service_by_local(self.diet.is_local)
            if not service:
                ttk.Label(parent, text="No hay información de precios disponible", font=("Arial", 9)).pack(anchor=tk.W)
                return

            # Encabezados de la tabla
            headers_frame = ttk.Frame(parent)
            headers_frame.pack(fill=tk.X, pady=(0, 8))
            
            ttk.Label(headers_frame, text="Servicio", font=("Arial", 9, "bold"), width=10, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(headers_frame, text="Cant.", font=("Arial", 9, "bold"), width=6, anchor=tk.CENTER).pack(side=tk.LEFT)
            ttk.Label(headers_frame, text="Precio Unit.", font=("Arial", 9, "bold"), width=10, anchor=tk.CENTER).pack(side=tk.LEFT)
            ttk.Label(headers_frame, text="Subtotal", font=("Arial", 9, "bold"), width=10, anchor=tk.CENTER).pack(side=tk.LEFT)

            # Datos de los servicios
            services_data = [
                ("🍳 Desayunos", self.diet.breakfast_count, service.breakfast_price),
                ("🍲 Almuerzos", self.diet.lunch_count, service.lunch_price),
                ("🍽️ Cenas", self.diet.dinner_count, service.dinner_price)
            ]

            # Precio de alojamiento según método de pago
            if self.diet.accommodation_payment_method == "CARD":
                accommodation_price = service.accommodation_card_price
                payment_info = "(Tarjeta)"
            else:
                accommodation_price = service.accommodation_cash_price
                payment_info = "(Efectivo)"
            
            services_data.append((f"🏨 Alojamientos {payment_info}", self.diet.accommodation_count, accommodation_price))

            total_general = 0
            for service_name, count, unit_price in services_data:
                row_frame = ttk.Frame(parent)
                row_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(row_frame, text=service_name, font=("Arial", 9), width=10, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=str(count), font=("Arial", 9), width=6, anchor=tk.CENTER).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"${unit_price:.2f}", font=("Arial", 9), width=10, anchor=tk.CENTER).pack(side=tk.LEFT)
                
                subtotal = count * unit_price
                total_general += subtotal
                ttk.Label(row_frame, text=f"${subtotal:.2f}", font=("Arial", 9), width=10, anchor=tk.CENTER).pack(side=tk.LEFT)

        except Exception as e:
            ttk.Label(parent, text=f"Error al cargar servicios: {str(e)}", font=("Arial", 9)).pack(anchor=tk.W)
    
    def create_status_and_total(self, parent):
        # Estado
        status_map = {
            "requested": "🟡 Solicitada",
            "liquidated": "🔵 Liquidada"
        }
        
        status_display = status_map.get(self.diet.status, self.diet.status)
        
        # Calcular total
        total = self.calculate_total()
        
        # Frame para estado
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Estado:", font=("Arial", 10, "bold"), width=8, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(status_frame, text=status_display, font=("Arial", 10)).pack(side=tk.LEFT, padx=(8, 0))
        
        # Frame para total
        total_frame = ttk.Frame(parent)
        total_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(total_frame, text="TOTAL:", font=("Arial", 11, "bold"), anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(total_frame, text=f"${total:.2f}", font=("Arial", 11, "bold"), foreground="green").pack(side=tk.LEFT, padx=(10, 0))
    
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