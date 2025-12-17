import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from traceback import print_exc
import traceback
from typing import List, Optional, Callable
from application.dtos.diet_dtos import DietResponseDTO, DietLiquidationResponseDTO
from application.services import user_service
from application.services.request_service import UserRequestService
from application.services.diet_service import DietAppService, DietService


class DietList(ttk.Frame):
    """
    Widget para mostrar listas de dietas (anticipos o liquidaciones) - CORREGIDO
    """
    
    def __init__(self, parent, list_type: str, request_user_service: UserRequestService, diet_service: DietAppService): 
        super().__init__(parent)
        self.list_type = list_type  # "advances" o "liquidations"
        self.selection_callback: Optional[Callable] = None
        self.request_user_service = request_user_service
        self.diet_service = diet_service
        self.sort_column = None
        self.sort_reverse = False
        self.current_data = []  
        self.create_widgets()
    
    def calculate_total(self, diet, is_local = None) -> float:
        """Calcula el total de una dieta basado en los precios del servicio"""
        try:            
            if not diet:
                return 0.0
            
            if not self.diet_service:
                return 0.0
            
            local = None

            if is_local is not None:
                local = is_local
            elif hasattr(diet, 'is_local'):
                local = diet.is_local
            else:
                local = True

            service = self.diet_service.get_diet_service_by_local(local) 
            
            if not service:
                return 0.0
            
            breakfast_count = 0
            lunch_count = 0
            dinner_count = 0
            accommodation_count = 0
            accommodation_payment_method = "CASH"

            if hasattr(diet, 'breakfast_count'):
                # Es un DietResponseDTO (anticipo)
                breakfast_count = diet.breakfast_count
                lunch_count = diet.lunch_count
                dinner_count = diet.dinner_count
                accommodation_count = diet.accommodation_count
                accommodation_payment_method = diet.accommodation_payment_method
            elif hasattr(diet, 'breakfast_count_liquidated'):
                # Es un DietLiquidationResponseDTO (liquidación)
                breakfast_count = diet.breakfast_count_liquidated
                lunch_count = diet.lunch_count_liquidated
                dinner_count = diet.dinner_count_liquidated
                accommodation_count = diet.accommodation_count_liquidated
                accommodation_payment_method = diet.accommodation_payment_method
            
            # Calcular total
            breakfast_total = breakfast_count * service.breakfast_price
            lunch_total = lunch_count * service.lunch_price
            dinner_total = dinner_count * service.dinner_price
            
            
            # Usar precio correcto según método de pago
            if diet.accommodation_payment_method == "CARD":
                if hasattr(diet, 'accommodation_count'):
                    accommodation_total = diet.accommodation_count * service.accommodation_card_price
                else: 
                    accommodation_total = diet.accommodation_count_liquidated * service.accommodation_card_price
            else:
                if hasattr(diet, 'accommodation_count'):
                    accommodation_total = diet.accommodation_count * service.accommodation_card_price
                else: 
                    accommodation_total = diet.accommodation_count_liquidated * service.accommodation_card_price
            
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
        

        if self.list_type == "all":
            columns = ["advance_number", "type", "description", "solicitante", 
                  "fecha_inicio", "fecha_fin", "monto", "estado"]  
            column_names = ["N° Anticipo", "Tipo", "Descripción", "Solicitante", 
                      "Fecha Inicio", "Fecha Fin", "Monto", "Estado"]
        elif self.list_type == "advances":
            columns = ["advance_number", "type", "description", "solicitante", 
                      "fecha_inicio", "fecha_fin", "monto"]
            column_names = ["N° Anticipo", "Tipo", "Descripción", "Solicitante", 
                          "Fecha Inicio", "Fecha Fin", "Monto"]
        else:
            columns = ["liquidation_number", "advance_number", "solicitante", 
                    "fecha_liquidacion", "desayunos", "almuerzos", "cenas", 
                    "alojamientos", "monto_liquidado"]
            column_names = ["N° Liquidación", "N° Anticipo", "Solicitante", 
                      "Fecha Liquidación", "Desayunos", "Almuerzos", "Cenas", 
                      "Alojamientos", "Monto Liquidado"]
        
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col, name in zip(columns, column_names):
            self.tree.heading(col, text=name)
            if col == "monto" or col == "monto_liquidado":
                self.tree.column(col, width=100, anchor="e")  
            elif col == "type":  
                self.tree.column(col, width=80, anchor="center")
            elif col in ["desayunos", "almuerzos", "cenas", "alojamientos"]:
                self.tree.column(col, width=80, anchor="center")
            else:
                self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección - CORREGIDO: usar el método correcto
        self.tree.bind("<<TreeviewSelect>>", self._on_selection)
    
    def _on_selection(self, event):
        """Maneja la selección de items """
        if not self.selection_callback:
            return
        
        selection = self.tree.selection()
        if not selection:
            self.selection_callback(None)
            return
        
        try:
            selected_item_id = selection[0]
            selected_index = self.tree.index(selected_item_id)

            # Obtener el objeto correspondiente de current_data
            if self.current_data and selected_index < len(self.current_data):
                selected_item = self.current_data[selected_index]
                self.selection_callback(selected_item)
            else:
                self.selection_callback(None)
                
        except Exception as e:
            print(f"Error en selección: {e}")
            traceback.print_exc()
            self.selection_callback(None)
    
    def _get_diet_type(self, diet):
        """Obtiene el tipo de dieta para mostrar en la columna"""
        if hasattr(diet, 'is_group'):
            return "👥 Grupal" if diet.is_group else "👤 Individual"
        return "Individual"
    
    def update_data(self, data: list, type):
        """Actualiza los datos en la lista"""
        self.current_display_type = type  
        
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_data = data or []  
        if not data:
            return
        
        if type == 1 or type == 0:
            for i, item in enumerate(data):
            # Para pestaña "all" o "advances"
                if hasattr(item, 'advance_number'):  
                    user = self.request_user_service.get_user_by_id(item.request_user_id)                    
                    total_amount = self.calculate_total(item)
                    diet_type = self._get_diet_type(item)
                    
                    # Para pestaña "all"
                    if self.list_type == "all":
                        
                        status_display = "Pendiente"  
                        if hasattr(item, 'status'):
                            status_display = item.status
                        
                        self.tree.insert("", "end", values=(
                            item.advance_number,
                            diet_type,
                            item.description,
                            f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                            item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                            item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                            f"${total_amount:.2f}" if total_amount is not None else "$0.00",
                            status_display  
                        ))
                    # Para pestaña "advances"   
                    elif self.list_type == "advances":
                        self.tree.insert("", "end", values=(
                            item.advance_number,
                            diet_type,
                            item.description,
                            f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                            item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                            item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                            f"${total_amount:.2f}" if total_amount is not None else "$0.00"
                        ))
        elif type == 2:  
            for item in data:
                if hasattr(item, 'liquidation_number'):

                    
                    # Obtener información completa
                    diet = self.diet_service.get_diet(item.diet_id) if self.diet_service else None
                    user = self.request_user_service.get_user_by_id(diet.request_user_id) if diet else None
                    
                    # Formatear datos para mostrar
                    solicitante = f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A"
                    fecha_liquidacion = item.liquidation_date.strftime("%d/%m/%Y") if item.liquidation_date else "N/A"
                    monto = self.calculate_total(item, diet.is_local)   # type: ignore
                    advance_number = diet.advance_number if diet else "N/A"
                    
                    self.tree.insert("", "end", values=(
                        item.liquidation_number,      
                        advance_number,               
                        solicitante,                 
                        fecha_liquidacion,            
                        item.breakfast_count_liquidated,  
                        item.lunch_count_liquidated,      
                        item.dinner_count_liquidated,     
                        item.accommodation_count_liquidated, 
                        monto                         
                    ))

    
    def bind_selection(self, callback: Callable):
        """Establece el callback para cuando se selecciona un item"""
        self.selection_callback = callback
    
    def get_selected_item(self):
        """Retorna el item seleccionado"""
        selection = self.tree.selection()
        if selection:
            selected_index = self.tree.index(selection[0])
            if selected_index < len(self.current_data):
                return self.current_data[selected_index]
        return None
    
    def clear_selection(self):
        """Limpia la selección actual"""
        self.tree.selection_remove(self.tree.selection())

    def filter_data(self, search_text: str):
        """Filtra los datos basado en el texto de búsqueda"""
        if not search_text:
            # Si no hay texto, mostrar todos los datos
            self._refresh_display(self.current_data)
            return
        
        search_lower = search_text.lower()
        filtered_data = []
        
        for item in self.current_data:
            # Buscar en todos los valores de las columnas
            if self._item_matches_search(item, search_lower):
                filtered_data.append(item)
        
        self._refresh_display(filtered_data)

    def _item_matches_search(self, item, search_lower: str) -> bool:
        """Verifica si el item coincide con el texto de búsqueda - CORREGIDO PARA LIQUIDACIONES"""
        try:
            # BÚSQUEDA ESPECÍFICA PARA LIQUIDACIONES
            if self.list_type == "liquidations" and hasattr(item, 'liquidation_number'):
                # Buscar en campos directos de la liquidación
                if (self._value_matches_search(item.liquidation_number, search_lower) or
                    self._value_matches_search(item.breakfast_count_liquidated, search_lower) or
                    self._value_matches_search(item.lunch_count_liquidated, search_lower) or
                    self._value_matches_search(item.dinner_count_liquidated, search_lower) or
                    self._value_matches_search(item.accommodation_count_liquidated, search_lower)):
                    return True
                
                # Buscar en la dieta asociada
                diet = self.diet_service.get_diet(item.diet_id) if self.diet_service else None
                if diet:
                    # Buscar en número de anticipo
                    if self._value_matches_search(diet.advance_number, search_lower):
                        return True
                    
                    # Buscar en nombre del solicitante
                    user = self.request_user_service.get_user_by_id(diet.request_user_id)
                    if user and hasattr(user, 'fullname'):
                        if self._value_matches_search(user.fullname, search_lower):
                            return True
                    
                    # Buscar en descripción de la dieta
                    if self._value_matches_search(diet.description, search_lower):
                        return True
                
                # Buscar en fecha de liquidación
                if (item.liquidation_date and 
                    self._value_matches_search(item.liquidation_date.strftime("%d/%m/%Y"), search_lower)):
                    return True
                    
                return False

            # LÓGICA ORIGINAL PARA ANTICIPOS Y TODAS LAS DIETAS
            if hasattr(item, '__dict__'):
                # Para objetos, revisar todos sus atributos
                for attr_name, attr_value in item.__dict__.items():
                    if self._value_matches_search(attr_value, search_lower):
                        return True
            else:
                # Para otros tipos de datos
                if self._value_matches_search(str(item), search_lower):
                    return True
                    
            # Búsqueda específica para campos comunes de dietas
            common_fields = ['advance_number', 'liquidation_number', 'description', 'status']
            for field in common_fields:
                if hasattr(item, field):
                    value = getattr(item, field)
                    if self._value_matches_search(value, search_lower):
                        return True
            
            # Buscar en el nombre del solicitante
            if hasattr(item, 'request_user_id'):
                user = self.request_user_service.get_user_by_id(item.request_user_id)
                if user and hasattr(user, 'fullname'):
                    if self._value_matches_search(user.fullname, search_lower):
                        return True
            
            # Buscar en montos
            if hasattr(item, 'total_amount') or hasattr(item, 'amount'):
                amount = getattr(item, 'total_amount', getattr(item, 'amount', None))
                if self._value_matches_search(amount, search_lower):
                    return True
                    
        except Exception as e:
            print(f"Error en búsqueda de item: {e}")
        
        return False

    def _value_matches_search(self, value, search_lower: str) -> bool:
        """Verifica si un valor individual coincide con la búsqueda"""
        if value is None:
            return False
        
        try:
            if isinstance(value, (int, float)):
                # Para números, buscar en su representación string
                return search_lower in str(value)
            elif isinstance(value, str):
                return search_lower in value.lower()
            elif hasattr(value, 'strftime'):  # Para objetos datetime
                return search_lower in value.strftime("%d/%m/%Y").lower()
            else:
                return search_lower in str(value).lower()
        except:
            return False

    def _refresh_display(self, data: list):
        """Actualiza la visualización con los datos proporcionados - OPTIMIZADO"""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Mostrar nuevos datos
        if not data:
            return
            
        if self.list_type == "all":
            # Lógica para pestaña "Todas"
            for item in data:
                user = self.request_user_service.get_user_by_id(item.request_user_id)                    
                total_amount = self.calculate_total(item)
                diet_type = self._get_diet_type(item)
                
                status_display = "Pendiente"  
                if hasattr(item, 'status'):
                    status_display = "Liquidada" if item.status == "liquidated" else "Solicitada"
                
                self.tree.insert("", "end", values=(
                    item.advance_number,
                    diet_type,
                    item.description,
                    f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                    item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                    item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                    f"${total_amount:.2f}" if total_amount is not None else "$0.00",
                    status_display  
                ))
        elif self.list_type == "advances":
            # Lógica para pestaña "Anticipos"
            for item in data:
                user = self.request_user_service.get_user_by_id(item.request_user_id)                    
                total_amount = self.calculate_total(item)
                diet_type = self._get_diet_type(item)
                
                self.tree.insert("", "end", values=(
                    item.advance_number,
                    diet_type,
                    item.description,
                    f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                    item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                    item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                    f"${total_amount:.2f}" if total_amount is not None else "$0.00"
                ))
        elif self.list_type == "liquidations":
            # Lógica MEJORADA para pestaña "Liquidaciones"
            for item in data:
                diet = self.diet_service.get_diet(item.diet_id) if self.diet_service else None
                user = self.request_user_service.get_user_by_id(diet.request_user_id) if diet else None
                
                solicitante = f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A"
                fecha_liquidacion = item.liquidation_date.strftime("%d/%m/%Y") if item.liquidation_date else "N/A"
                monto = self.calculate_total(item, diet.is_local if diet else True)
                advance_number = diet.advance_number if diet else "N/A"
                
                self.tree.insert("", "end", values=(
                    item.liquidation_number,      
                    advance_number,               
                    solicitante,                 
                    fecha_liquidacion,            
                    item.breakfast_count_liquidated,  
                    item.lunch_count_liquidated,      
                    item.dinner_count_liquidated,     
                    item.accommodation_count_liquidated, 
                    f"${monto:.2f}" if monto is not None else "$0.00"
                ))

   