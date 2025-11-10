import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable
from application.dtos.diet_dtos import DietResponseDTO, DietLiquidationResponseDTO
from application.services import user_service
from application.services.request_service import UserRequestService
from application.services.diet_service import DietAppService, DietService

class DietList(ttk.Frame):
    """
    Widget para mostrar listas de dietas (anticipos o liquidaciones)
    """
    
    def __init__(self, parent, list_type: str, request_user_service: UserRequestService, diet_service: DietAppService): 
        super().__init__(parent)
        self.list_type = list_type  # "advances" o "liquidations"
        self.selection_callback: Optional[Callable] = None
        self.request_user_service = request_user_service
        self.diet_service = diet_service          
        self.create_widgets()
    
    def calculate_total(self, diet: DietResponseDTO) -> float:
        """Calcula el total de una dieta basado en los precios del servicio"""
        try:            
            if not diet:
                return 0.0
            
            if not self.diet_service:
                return 0.0
            
            # Obtener el servicio de dieta según si es local o no
            service = self.diet_service.get_diet_service_by_local(diet.is_local)
            
            if not service:
                return 0.0
            
            # Calcular total
            breakfast_total = diet.breakfast_count * service.breakfast_price
            lunch_total = diet.lunch_count * service.lunch_price
            dinner_total = diet.dinner_count * service.dinner_price
            accommodation_total = diet.accommodation_count * service.accommodation_cash_price
            
            total = breakfast_total + lunch_total + dinner_total + accommodation_total            
            return total
            
        except Exception as e:
            print(f"ERROR calculando total: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        if self.list_type == "advances":
            columns = ["advance_number", "description", "solicitante", "fecha_inicio", 
                      "fecha_fin", "monto"]
            column_names = ["N° Anticipo", "Descripción", "Solicitante", "Fecha Inicio", 
                          "Fecha Fin", "Monto"]
        else:
            columns = ["liquidation_number", "diet_id", "fecha_liquidacion", 
                      "monto_liquidado"]
            column_names = ["N° Liquidación", "ID Dieta", "Fecha Liquidación", 
                          "Monto Liquidado"]
        
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col, name in zip(columns, column_names):
            self.tree.heading(col, text=name)
            if col == "monto" or col == "monto_liquidado":
                self.tree.column(col, width=100, anchor="e")  
            else:
                self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.tree.bind("<<TreeviewSelect>>", self.on_selection)
    
    def update_data(self, data: list):
        """Actualiza los datos en la lista"""
        
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_data = data

        # Verificar si data es None o vacía
        if not data:
            return
        
        # Agregar nuevos datos
        for i, item in enumerate(data):
            
            if self.list_type == "advances":
                if hasattr(item, 'advance_number'):  # Verificar si es DietResponseDTO
                    user = self.request_user_service.get_user_by_id(item.request_user_id)                    
                    # Calcular el total usando nuestra nueva función
                    total_amount = self.calculate_total(item)
                    
                    # Insertar en treeview
                    self.tree.insert("", "end", values=(
                        item.advance_number,
                        item.description,
                        f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                        item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                        item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                        f"${total_amount:.2f}" if total_amount is not None else "$0.00"
                    ))
                else:
                    pass

            elif self.list_type == "liquidations":
                if hasattr(item, 'liquidation_number'):  # Verificar si es DietLiquidationResponseDTO
                    self.tree.insert("", "end", values=(
                        item.liquidation_number,
                        item.diet_id,
                        item.liquidation_date.strftime("%d/%m/%Y %H:%M") if item.liquidation_date else "N/A",
                        f"${item.liquidated_amount:.2f}" if item.liquidated_amount else "$0.00"
                    ))
    
    def bind_selection(self, callback: Callable):
        """Establece el callback para cuando se selecciona un item"""
        self.selection_callback = callback
    
    def on_selection(self, event):
        """Maneja la selección de items"""

        if not self.selection_callback:
            return
        
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_index = self.tree.index(selection[0])

        # Obtener el objeto correspondiente de current_data
        if hasattr(self, 'current_data') and self.current_data and selected_index < len(self.current_data):
            selected_item = self.current_data[selected_index]
            self.selection_callback(selected_item)
        else:
            self.selection_callback(None) 
    
    def get_selected_item(self):
        """Retorna el item seleccionado"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])
        return None
    
    def clear_selection(self):
        """Limpia la selección actual"""
        self.tree.selection_remove(self.tree.selection())