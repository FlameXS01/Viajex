import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable
from application.dtos.diet_dtos import DietResponseDTO, DietLiquidationResponseDTO

class DietList(ttk.Frame):
    """
    Widget para mostrar listas de dietas (anticipos o liquidaciones)
    """
    
    def __init__(self, parent, list_type: str):
        super().__init__(parent)
        self.list_type = list_type  # "advances" o "liquidations"
        self.selection_callback: Optional[Callable] = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        if self.list_type == "advances":
            columns = ["id", "advance_number", "description", "solicitante", "fecha_inicio", 
                      "fecha_fin", "estado", "monto"]
            column_names = ["ID", "N° Anticipo", "Descripción", "Solicitante", "Fecha Inicio", 
                          "Fecha Fin", "Estado", "Monto"]
        else:
            columns = ["id", "liquidation_number", "diet_id", "fecha_liquidacion", 
                      "monto_liquidado", "estado"]
            column_names = ["ID", "N° Liquidación", "ID Dieta", "Fecha Liquidación", 
                          "Monto Liquidado", "Estado"]
        
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col, name in zip(columns, column_names):
            self.tree.heading(col, text=name)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.tree.bind("<<TreeviewSelect>>", self.on_selection)
    
    def update_data(self, data: List):
        """Actualiza los datos en la lista"""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar nuevos datos
        for item in data:
            if self.list_type == "advances" and isinstance(item, DietResponseDTO):
                self.tree.insert("", "end", values=(
                    item.id,
                    item.advance_number,
                    item.description,
                    f"Solicitante {item.request_user_id}",  # En realidad debería ser el nombre
                    item.start_date.strftime("%d/%m/%Y"),
                    item.end_date.strftime("%d/%m/%Y"),
                    self._get_status_text(item.status),
                    f"${item.total_amount:.2f}" if item.total_amount else "$0.00"
                ))
            elif self.list_type == "liquidations" and isinstance(item, DietLiquidationResponseDTO):
                self.tree.insert("", "end", values=(
                    item.id,
                    item.liquidation_number,
                    item.diet_id,
                    item.liquidation_date.strftime("%d/%m/%Y %H:%M"),
                    f"${item.liquidated_amount:.2f}" if item.liquidated_amount else "$0.00",
                    "Liquidado"
                ))
    
    def _get_status_text(self, status: str) -> str:
        """Convierte el estado a texto legible"""
        status_map = {
            "requested": "Solicitado",
            "liquidated": "Liquidado",
            "partially_liquidated": "Parcialmente Liquidado"
        }
        return status_map.get(status, status)
    
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
        
        # Obtener datos del item seleccionado
        item = self.tree.item(selection[0])
        values = item["values"]
        
        # En una implementación real, aquí buscarías el objeto completo por ID
        # Por ahora, creamos un objeto simple con los datos básicos
        if self.list_type == "advances":
            diet = DietResponseDTO(
                id=values[0],
                advance_number=values[1],
                description=values[2],
                request_user_id=0,  # Esto debería venir de los datos
                start_date=None,  # Debería convertirse de string a date
                end_date=None,
                status=self._get_status_key(values[6]),
                is_local=True,
                is_group=False,
                diet_service_id=0,
                breakfast_count=0,
                lunch_count=0,
                dinner_count=0,
                accommodation_count=0,
                accommodation_payment_method="CASH",
                accommodation_card_id=None,
                created_at=None,
                total_amount=0.0
            )
            self.selection_callback(diet)
        else:
            # Para liquidaciones, podrías hacer algo similar
            pass
    
    def _get_status_key(self, status_text: str) -> str:
        """Convierte texto de estado a clave"""
        status_map = {
            "Solicitado": "requested",
            "Liquidado": "liquidated", 
            "Parcialmente Liquidado": "partially_liquidated"
        }
        return status_map.get(status_text, "requested")
    
    def get_selected_item(self):
        """Retorna el item seleccionado"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])
        return None
    
    def clear_selection(self):
        """Limpia la selección actual"""
        self.tree.selection_remove(self.tree.selection())