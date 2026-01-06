import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from traceback import print_exc
import traceback
from typing import List, Optional, Callable

from scipy.fftpack import cc_diff
from application.dtos.diet_dtos import DietResponseDTO, DietLiquidationResponseDTO
from application.services import user_service
from application.services.department_service import DepartmentService
from application.services.request_service import UserRequestService
from application.services.diet_service import DietAppService, DietService
from datetime import datetime, timezone, date

class DietList(ttk.Frame):
    """
    Widget para mostrar listas de dietas (anticipos o liquidaciones) - CORREGIDO
    """
    
    def __init__(self, parent, list_type: str, request_user_service: UserRequestService, diet_service: DietAppService, departament_service: DepartmentService): 
        super().__init__(parent)
        self.list_type = list_type  # "advances" o "liquidations"
        self.selection_callback: Optional[Callable] = None
        self.request_user_service = request_user_service
        self.diet_service = diet_service
        self.departament_service = departament_service
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
                # si tiene accommodation_count es dieta sino es liquidacion 
                if hasattr(diet, 'accommodation_count'):
                    accommodation_total = diet.accommodation_count * service.accommodation_card_price
                else:
                    # si tiene total_pay se usa ese precio en vez del precio en el servicio
                    if hasattr(diet, 'total_pay'):
                        accommodation_total = diet.accommodation_count_liquidated * diet.total_pay
                    else:
                        accommodation_total = diet.accommodation_count_liquidated * service.accommodation_card_price
            # Cuando es en efectivo
            else:
                if hasattr(diet, 'accommodation_count'):
                    accommodation_total = diet.accommodation_count * service.accommodation_cash_price
                else: 
                    if hasattr(diet, 'total_pay'):
                        accommodation_total = diet.accommodation_count_liquidated * diet.total_pay
                    else:
                        accommodation_total = diet.accommodation_count_liquidated * service.accommodation_cash_price
            
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
        
        # Definir columnas según el tipo de lista
        if self.list_type == "all":
            columns = ["advance_number", "description", "solicitante", "departamento",
                      "fecha_inicio", "fecha_fin", "monto", "estado"]  
            column_names = ["N° Anticipo", "Descripción", "Solicitante", "Departamento",
                          "Fecha Inicio", "Fecha Fin", "Monto", "Estado"]
        elif self.list_type == "advances":
            columns = ["advance_number", "description", "solicitante", "departamento",
                      "fecha_inicio", "fecha_fin", "monto"]
            column_names = ["N° Anticipo", "Descripción", "Solicitante", "Departamento",
                          "Fecha Inicio", "Fecha Fin", "Monto"]
        else:
            columns = ["liquidation_number", "advance_number", "solicitante", "departamento",
                      "fecha_liquidacion", "desayunos", "almuerzos", "cenas", 
                      "alojamientos", "monto_liquidado"]
            column_names = ["N° Liquidación", "N° Anticipo", "Solicitante", "Departamento",
                          "Fecha Liquidación", "Desayunos", "Almuerzos", "Cenas", 
                          "Alojamientos", "Monto Liquidado"]
        
        # Crear el Treeview
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col, name in zip(columns, column_names):
            self.tree.heading(col, text=name)
            # Ajustar ancho de columnas según contenido
            if col in ["monto", "monto_liquidado"]:
                self.tree.column(col, width=100, anchor="e")  # Montos alineados a la derecha
            elif col in ["desayunos", "almuerzos", "cenas", "alojamientos"]:
                self.tree.column(col, width=80, anchor="center")  # Cantidades centradas
            elif col == "advance_number" or col == "liquidation_number":
                self.tree.column(col, width=80, anchor="center")  # Números centrados
            else:
                self.tree.column(col, width=120)  # Ancho por defecto
        
        # Configurar Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar elementos
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar evento de selección
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
        
        # Para pestañas "all" o "advances"
        if type == 1 or type == 0:
            for i, item in enumerate(data):
                if hasattr(item, 'advance_number'):  
                    user = self.request_user_service.get_user_by_id(item.request_user_id)                    
                    total_amount = self.calculate_total(item)
                    
                    # Obtener departamento del usuario (si existe)
                    departamento = "N/A"
                    if user and hasattr(user, 'department_id'):
                        departamento = self.departament_service.get_department_by_id(user.department_id).name
                    
                    # Para pestaña "all"
                    if self.list_type == "all":
                        status_display = "Pendiente"  
                        if hasattr(item, 'status'):
                            status_display = item.status
                        
                        item_id = self.tree.insert("", "end", values=(
                            item.advance_number,
                            item.description,
                            f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                            departamento,
                            item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                            item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                            f"${total_amount:.2f}" if total_amount is not None else "$0.00",
                            status_display  
                        ))
                    # Para pestaña "advances"   
                    elif self.list_type == "advances":
                        # Obtener departamento del usuario (si existe)
                        departamento = "N/A"
                        if user and hasattr(user, 'department_id'):
                            departamento = self.departament_service.get_department_by_id(user.department_id).name
                        
                        # Determinar color basado en antigüedad
                        bg_color = self._get_row_color_based_on_age(item)
                        
                        item_id = self.tree.insert("", "end", values=(
                            item.advance_number,
                            item.description,
                            f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                            departamento,
                            item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                            item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                            f"${total_amount:.2f}" if total_amount is not None else "$0.00"
                        ))
                        
                        # Aplicar color de fondo si corresponde
                        if bg_color:
                            # Crear un tag único para este color específico
                            tag_name = f"color_{bg_color.replace('#', '')}"
                            self.tree.item(item_id, tags=(tag_name,))
                            self.tree.tag_configure(tag_name, background=bg_color)
        
        # Para pestaña "liquidations" (type == 2)
        elif type == 2:  
            for item in data:
                if hasattr(item, 'liquidation_number'):
                    # Obtener información completa
                    diet = self.diet_service.get_diet(item.diet_id) if self.diet_service else None
                    user = self.request_user_service.get_user_by_id(diet.request_user_id) if diet else None
                    
                    # Obtener departamento del usuario (si existe) - CORREGIDO
                    departamento = "N/A"
                    if user and hasattr(user, 'department_id'):
                        dept = self.departament_service.get_department_by_id(user.department_id)
                        departamento = dept.name if dept else "N/A"
                    
                    # Formatear datos para mostrar
                    solicitante = f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A"
                    fecha_liquidacion = item.liquidation_date.strftime("%d/%m/%Y") if item.liquidation_date else "N/A"
                    monto = self.calculate_total(item, diet.is_local if diet else True)   # type: ignore
                    advance_number = diet.advance_number if diet else "N/A"
                    
                    self.tree.insert("", "end", values=(
                        item.liquidation_number,      
                        advance_number,               
                        solicitante,                 
                        departamento,                                               # Columna departamento
                        fecha_liquidacion,            
                        item.breakfast_count_liquidated,  
                        item.lunch_count_liquidated,      
                        item.dinner_count_liquidated,     
                        item.accommodation_count_liquidated, 
                        f"${monto:.2f}" if monto is not None else "$0.00"
                    ))
        
        if self.list_type == "advances":
            self.refresh_colors()
        
    def bind_selection(self, callback: Callable):
        """Establece el callback para cuando se selecciona un item"""
        self.selection_callback = callback
    
    def _get_row_color_based_on_age(self, item):
        """Determina el color de la fila basado en la antigüedad de la solicitud"""
        bg_color = ""
        if hasattr(item, 'start_date') and item.start_date:
            from datetime import datetime, date
            
            try:
                # Convertir start_date a datetime si es date
                if isinstance(item.start_date, date):
                    start_datetime = datetime.combine(item.start_date, datetime.min.time())
                else:
                    start_datetime = item.start_date
                
                now = datetime.now()
                hours_diff = (now - start_datetime).total_seconds() / 3600
                
                if hours_diff > 72:
                    bg_color = "#E24F4A"  # Rojo
                elif hours_diff > 48:
                    bg_color = "#e6e622"  # Amarillo
                    
            except Exception as e:
                print(f"Error calculando diferencia de horas: {e}")
        
        return bg_color

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
            # Si no hay texto, mostrar todos los datos ORIGINALES (no filtrados)
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
                    if user:
                        if hasattr(user, 'fullname') and self._value_matches_search(user.fullname, search_lower):
                            return True
                        
                        # BUSCAR EN EL DEPARTAMENTO DEL USUARIO (NUEVO)
                        if hasattr(user, 'department_id') and user.department_id:
                            dept = self.departament_service.get_department_by_id(user.department_id)
                            if dept and hasattr(dept, 'name') and self._value_matches_search(dept.name, search_lower):
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
            
            # Buscar en el nombre del solicitante Y DEPARTAMENTO
            if hasattr(item, 'request_user_id'):
                user = self.request_user_service.get_user_by_id(item.request_user_id)
                if user:
                    if hasattr(user, 'fullname') and self._value_matches_search(user.fullname, search_lower):
                        return True
                    
                    # BUSCAR EN EL DEPARTAMENTO DEL USUARIO (NUEVO)
                    if hasattr(user, 'department_id') and user.department_id:
                        dept = self.departament_service.get_department_by_id(user.department_id)
                        if dept and hasattr(dept, 'name') and self._value_matches_search(dept.name, search_lower):
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
                
                # Obtener departamento del usuario (si existe) - CORREGIDO
                departamento = "N/A"
                if user and hasattr(user, 'department_id'):
                    dept = self.departament_service.get_department_by_id(user.department_id)
                    departamento = dept.name if dept else "N/A"
                
                status_display = "Pendiente"  
                if hasattr(item, 'status'):
                    status_display = "Liquidada" if item.status == "liquidated" else "Solicitada"
                
                item_id = self.tree.insert("", "end", values=(
                    item.advance_number,
                    item.description,
                    f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                    departamento,
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
                
                # Obtener departamento del usuario (si existe) - CORREGIDO
                departamento = "N/A"
                if user and hasattr(user, 'department_id'):
                    dept = self.departament_service.get_department_by_id(user.department_id)
                    departamento = dept.name if dept else "N/A"
                
                # Determinar color basado en antigüedad
                bg_color = self._get_row_color_based_on_age(item)
                
                item_id = self.tree.insert("", "end", values=(
                    item.advance_number,
                    item.description,
                    f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A",  
                    departamento,
                    item.start_date.strftime("%d/%m/%Y") if item.start_date else "N/A",
                    item.end_date.strftime("%d/%m/%Y") if item.end_date else "N/A",
                    f"${total_amount:.2f}" if total_amount is not None else "$0.00"
                ))
                
                # Aplicar color de fondo si corresponde
                if bg_color:
                    # Crear un tag único para este color específico
                    tag_name = f"color_{bg_color.replace('#', '')}"
                    self.tree.item(item_id, tags=(tag_name,))
                    self.tree.tag_configure(tag_name, background=bg_color)
        
        # AGREGAR MANEJO DE LIQUIDACIONES
        elif self.list_type == "liquidations":
            for item in data:
                if hasattr(item, 'liquidation_number'):
                    diet = self.diet_service.get_diet(item.diet_id) if self.diet_service else None
                    user = self.request_user_service.get_user_by_id(diet.request_user_id) if diet else None
                    
                    # Obtener departamento del usuario (si existe) - CORREGIDO
                    departamento = "N/A"
                    if user and hasattr(user, 'department_id'):
                        dept = self.departament_service.get_department_by_id(user.department_id)
                        departamento = dept.name if dept else "N/A"
                    
                    solicitante = f"{user.fullname}" if user and hasattr(user, 'fullname') else "N/A"
                    fecha_liquidacion = item.liquidation_date.strftime("%d/%m/%Y") if item.liquidation_date else "N/A"
                    monto = self.calculate_total(item, diet.is_local if diet else True)
                    advance_number = diet.advance_number if diet else "N/A"
                    
                    self.tree.insert("", "end", values=(
                        item.liquidation_number,      
                        advance_number,               
                        solicitante,                 
                        departamento,                 
                        fecha_liquidacion,            
                        item.breakfast_count_liquidated,  
                        item.lunch_count_liquidated,      
                        item.dinner_count_liquidated,     
                        item.accommodation_count_liquidated, 
                        f"${monto:.2f}" if monto is not None else "$0.00"
                    ))

    def refresh_colors(self):
        """Refresca los colores de todas las filas basado en su antigüedad"""
        if self.list_type != "advances":
            return
            
        for i, item_id in enumerate(self.tree.get_children()):
            if i < len(self.current_data):
                item = self.current_data[i]
                bg_color = self._get_row_color_based_on_age(item)
                
                # Limpiar tags existentes
                current_tags = self.tree.item(item_id, 'tags')
                if current_tags:
                    # Opcional: puedes eliminar los tags antiguos
                    pass
                
                # Aplicar nuevo color si corresponde
                if bg_color:
                    tag_name = f"color_{bg_color.replace('#', '')}"
                    self.tree.item(item_id, tags=(tag_name,))
                    self.tree.tag_configure(tag_name, background=bg_color)
                else:
                    # Si no debe tener color, quitar tags
                    self.tree.item(item_id, tags=())