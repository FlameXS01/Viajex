# application/controllers/diet_controller.py
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

from application.services.diet_service import DietAppService
from application.dtos.diet_dtos import (
    DietServiceResponseDTO,
    DietServiceCreateDTO,
    DietServiceUpdateDTO,
    DietCreateDTO,
    DietUpdateDTO,
    DietResponseDTO,
    DietLiquidationCreateDTO,
    DietLiquidationUpdateDTO,
    DietLiquidationResponseDTO,
    DietMemberCreateDTO,
    DietMemberResponseDTO,
    DietCalculationDTO,
    DietWithLiquidationDTO,
    DietCounterDTO
)


class DietController:
    """

    Controlador para el módulo de dietas.
    Maneja las solicitudes y coordina con el servicio de aplicación.

    """
    
    def __init__(self, diet_service: DietAppService):
        self.diet_service = diet_service

    # ===== SERVICIOS DE DIETA (PRECIOS) =====
    
    def get_diet_service_by_local(self, is_local: bool) -> Optional[DietServiceResponseDTO]:
        """

        Obtiene el servicio de dieta por localidad

        """
        return self.diet_service.get_diet_service_by_local(is_local)
    
    def list_all_diet_services(self) -> List[DietServiceResponseDTO]:
        """

        Lista todos los servicios de dieta

        """
        return self.diet_service.list_all_diet_services()
    
    def create_diet_service(self, create_dto: DietServiceCreateDTO) -> DietServiceResponseDTO:
        """

        Crea un nuevo servicio de dieta

        """
        return self.diet_service.create_diet_service(create_dto)
    
    def update_diet_service(self, service_id: int, update_dto: DietServiceUpdateDTO) -> Optional[DietServiceResponseDTO]:
        """

        Actualiza un servicio de dieta existente

        """
        return self.diet_service.update_diet_service(service_id, update_dto)

    # ===== DIETAS (ANTICIPOS) =====
    
    def create_diet(self, create_dto: DietCreateDTO) -> DietResponseDTO:
        """

        Crea un nuevo anticipo de dieta

        """
        return self.diet_service.create_diet(create_dto)
    
    def get_diet(self, diet_id: int) -> Optional[DietResponseDTO]:
        """

        Obtiene una dieta por ID

        """
        return self.diet_service.get_diet(diet_id)
    
    def list_diets(self, status: Optional[str] = None, request_user_id: Optional[int] = None) -> List[DietResponseDTO]:
        """

        Lista dietas con filtros opcionales

        """
        return self.diet_service.list_diets(status, request_user_id)
    
    def list_diets_by_status(self, status: str) -> List[DietResponseDTO]:
        """

        Lista dietas por estado específico

        """
        return self.diet_service.list_diets_by_status(status)
    
    def list_diets_pending_liquidation(self) -> List[DietResponseDTO]:
        """

        Lista dietas pendientes de liquidación

        """
        return self.diet_service.list_diets_pending_liquidation()
    
    def update_diet(self, diet_id: int, update_dto: DietUpdateDTO) -> Optional[DietResponseDTO]:
        """

        Actualiza una dieta existente

        """
        return self.diet_service.update_diet(diet_id, update_dto)
    
    def delete_diet(self, diet_id: int) -> bool:
        """

        Elimina una dieta

        """
        return self.diet_service.delete_diet(diet_id)
    
    def get_last_advance_number(self) -> int:
        """

        Obtiene el último número de anticipo utilizado

        """
        return self.diet_service.get_last_advance_number()
    
    def reset_advance_numbers(self) -> bool:
        """

        Reinicia los números de anticipo

        """
        return self.diet_service.reset_advance_numbers()

    # ===== LIQUIDACIONES =====
    
    def create_diet_liquidation(self, create_dto: DietLiquidationCreateDTO) -> DietLiquidationResponseDTO:
        """

        Crea una liquidación para una dieta

        """
        return self.diet_service.create_diet_liquidation(create_dto)
    
    def get_diet_liquidation(self, liquidation_id: int) -> Optional[DietLiquidationResponseDTO]:
        """

        Obtiene una liquidación por ID

        """
        return self.diet_service.get_diet_liquidation(liquidation_id)
    
    def get_liquidation_by_diet(self, diet_id: int) -> Optional[DietLiquidationResponseDTO]:
        """

        Obtiene la liquidación asociada a una dieta

        """
        return self.diet_service.get_liquidation_by_diet(diet_id)
    
    def list_liquidations_by_date_range(self, start_date: date, end_date: date) -> List[DietLiquidationResponseDTO]:
        """

        Lista liquidaciones por rango de fechas

        """
        return self.diet_service.list_liquidations_by_date_range(start_date, end_date)
    
    def update_diet_liquidation(self, liquidation_id: int, update_dto: DietLiquidationUpdateDTO) -> Optional[DietLiquidationResponseDTO]:
        """

        Actualiza una liquidación existente

        """
        return self.diet_service.update_diet_liquidation(liquidation_id, update_dto)
    
    def delete_diet_liquidation(self, liquidation_id: int) -> bool:
        """

        Elimina una liquidación

        """
        return self.diet_service.delete_diet_liquidation(liquidation_id)
    
    def get_last_liquidation_number(self) -> int:
        """

        Obtiene el último número de liquidación utilizado

        """
        return self.diet_service.get_last_liquidation_number()
    
    def reset_liquidation_numbers(self) -> bool:
        """

        Reinicia los números de liquidación

        """
        return self.diet_service.reset_liquidation_numbers()

    # ===== MIEMBROS DE DIETA GRUPAL =====
    
    def add_diet_member(self, create_dto: DietMemberCreateDTO) -> DietMemberResponseDTO:
        """
        
        Agrega un miembro a una dieta grupal

        """
        return self.diet_service.add_diet_member(create_dto)
    
    def remove_diet_member(self, member_id: int) -> bool:
        """

        Elimina un miembro de una dieta grupal

        """
        return self.diet_service.remove_diet_member(member_id)
    
    def list_diet_members(self, diet_id: int) -> List[DietMemberResponseDTO]:
        """

        Lista miembros de una dieta grupal

        """
        return self.diet_service.list_diet_members(diet_id)

    # ===== OPERACIONES ESPECIALES =====
    
    def calculate_diet_amount(self, calculation_data: Dict[str, Any]) -> DietCalculationDTO:
        """

        Calcula el monto total de una dieta

        """
        return self.diet_service.calculate_diet_amount(calculation_data)
    
    def reset_all_counters(self) -> bool:
        """

        Reinicia todos los contadores (anticipos y liquidaciones)

        """
        return self.diet_service.reset_all_counters()
    
    def get_diet_with_liquidation(self, diet_id: int) -> Optional[DietWithLiquidationDTO]:
        """

        Obtiene una dieta con su liquidación (si existe)

        """
        return self.diet_service.get_diet_with_liquidation(diet_id)
    
    def get_counters_info(self) -> DietCounterDTO:
        """

        Obtiene información de los contadores
        """
        
        return self.diet_service.get_counters_info()