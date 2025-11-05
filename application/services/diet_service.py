# application/services/diet_service.py
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date, datetime

from core.entities.diet import Diet, DietStatus
from core.entities.diet_service import DietService
from core.entities.diet_liquidation import DietLiquidation
from core.entities.diet_member import DietMember
from core.repositories.diet_repository import DietRepository
from core.repositories.diet_service_repository import DietServiceRepository
from core.repositories.diet_liquidation_repository import DietLiquidationRepository
from core.repositories.diet_member_repository import DietMemberRepository
from core.repositories.request_user_repository import RequestUserRepository

from core.use_cases.diets.diet_services.get_diet_service_by_local import GetDietServiceByLocalUseCase
from core.use_cases.diets.diet_services.list_all_diet_services import ListAllDietServicesUseCase
from core.use_cases.diets.diets.create_diet import CreateDietUseCase
from core.use_cases.diets.diets.get_diet import GetDietUseCase
from core.use_cases.diets.diets.list_diets_by_status import ListDietsByStatusUseCase
from core.use_cases.diets.diets.list_diets_pending_liquidation import ListDietsPendingLiquidationUseCase
from core.use_cases.diets.diets.update_diet import UpdateDietUseCase
from core.use_cases.diets.diets.delete_diet import DeleteDietUseCase
from core.use_cases.diets.diets.get_last_advance_number import GetLastAdvanceNumberUseCase
from core.use_cases.diets.diets.reset_advance_numbers import ResetAdvanceNumbersUseCase
from core.use_cases.diets.diet_liquidations.create_diet_liquidation import CreateDietLiquidationUseCase
from core.use_cases.diets.diet_liquidations.get_diet_liquidation import GetDietLiquidationUseCase
from core.use_cases.diets.diet_liquidations.get_liquidation_by_diet import GetLiquidationByDietUseCase
from core.use_cases.diets.diet_liquidations.list_liquidations_by_date_range import ListLiquidationsByDateRangeUseCase
from core.use_cases.diets.diet_liquidations.update_diet_liquidation import UpdateDietLiquidationUseCase
from core.use_cases.diets.diet_liquidations.delete_diet_liquidation import DeleteDietLiquidationUseCase
from core.use_cases.diets.diet_liquidations.get_last_liquidation_number import GetLastLiquidationNumberUseCase
from core.use_cases.diets.diet_liquidations.reset_liquidation_numbers import ResetLiquidationNumbersUseCase
from core.use_cases.diets.diet_members.add_diet_member import AddDietMemberUseCase
from core.use_cases.diets.diet_members.remove_diet_member import RemoveDietMemberUseCase
from core.use_cases.diets.diet_members.list_diet_members import ListDietMembersUseCase
from core.use_cases.diets.calculate_diet_amount import CalculateDietAmountUseCase
from core.use_cases.diets.list_diets import ListDietsUseCase
from core.use_cases.diets.reset_counters import ResetCountersUseCase

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


class DietAppService:
    """

    Servicio de aplicación para el módulo de dietas.
    Orquesta los casos de uso y adapta entre entidades y DTOs.
    
    """
    
    def __init__(
        self,
        diet_repository: DietRepository,
        diet_service_repository: DietServiceRepository,
        diet_liquidation_repository: DietLiquidationRepository,
        diet_member_repository: DietMemberRepository,
        request_user_repository: RequestUserRepository
    ):
        self.diet_repository = diet_repository
        self.diet_service_repository = diet_service_repository
        self.diet_liquidation_repository = diet_liquidation_repository
        self.diet_member_repository = diet_member_repository
        self.request_user_repository = request_user_repository

    # ===== SERVICIOS DE DIETA (PRECIOS) =====
    
    def get_diet_service_by_local(self, is_local: bool) -> Optional[DietServiceResponseDTO]:
        """Obtiene el servicio de dieta por localidad"""
        use_case = GetDietServiceByLocalUseCase(self.diet_service_repository)
        diet_service = use_case.execute(is_local)
        return self._to_diet_service_response_dto(diet_service) if diet_service else None
    
    def list_all_diet_services(self) -> List[DietServiceResponseDTO]:
        """Lista todos los servicios de dieta"""
        use_case = ListAllDietServicesUseCase(self.diet_service_repository)
        diet_services = use_case.execute()
        return [self._to_diet_service_response_dto(service) for service in diet_services]
    
    def create_diet_service(self, create_dto: DietServiceCreateDTO) -> DietServiceResponseDTO:
        """Crea un nuevo servicio de dieta"""
        diet_service = DietService(
            is_local=create_dto.is_local,
            breakfast_price=create_dto.breakfast_price,
            lunch_price=create_dto.lunch_price,
            dinner_price=create_dto.dinner_price,
            accommodation_cash_price=create_dto.accommodation_cash_price,
            accommodation_card_price=create_dto.accommodation_card_price
        )
        created_service = self.diet_service_repository.create(diet_service)
        return self._to_diet_service_response_dto(created_service)
    
    def update_diet_service(self, service_id: int, update_dto: DietServiceUpdateDTO) -> Optional[DietServiceResponseDTO]:
        """Actualiza un servicio de dieta existente"""
        diet_service = self.diet_service_repository.get_by_id(service_id)
        if not diet_service:
            return None
        
        # Actualizar campos permitidos
        update_data = {k: v for k, v in update_dto.__dict__.items() if v is not None}
        for field, value in update_data.items():
            if hasattr(diet_service, field):
                setattr(diet_service, field, value)
        
        updated_service = self.diet_service_repository.update(diet_service)
        return self._to_diet_service_response_dto(updated_service)

    # ===== DIETAS (ANTICIPOS) =====
    
    def create_diet(self, create_dto: DietCreateDTO) -> DietResponseDTO:
        """Crea un nuevo anticipo de dieta"""
        use_case = CreateDietUseCase(
            self.diet_repository,
            self.diet_service_repository,
            self.request_user_repository
        )
        
        diet_data = {
            'is_local': create_dto.is_local,
            'start_date': create_dto.start_date,
            'end_date': create_dto.end_date,
            'description': create_dto.description,
            'is_group': create_dto.is_group,
            'request_user_id': create_dto.request_user_id,
            'diet_service_id': create_dto.diet_service_id,
            'breakfast_count': create_dto.breakfast_count,
            'lunch_count': create_dto.lunch_count,
            'dinner_count': create_dto.dinner_count,
            'accommodation_count': create_dto.accommodation_count,
            'accommodation_payment_method': create_dto.accommodation_payment_method,
            'accommodation_card_id': create_dto.accommodation_card_id,
            'created_at': datetime.now()
        }
        
        diet = use_case.execute(diet_data)
        return self._to_diet_response_dto(diet)
    
    def get_diet(self, diet_id: int) -> Optional[DietResponseDTO]:
        """Obtiene una dieta por ID"""
        use_case = GetDietUseCase(self.diet_repository)
        diet = use_case.execute(diet_id)
        return self._to_diet_response_dto(diet) if diet else None
    
    def list_diets(self, status: Optional[str] = None, request_user_id: Optional[int] = None) -> List[DietResponseDTO]:
        """Lista dietas con filtros opcionales"""
        use_case = ListDietsUseCase(self.diet_repository)
        
        if status:
            diet_status = DietStatus(status)
            diets = use_case.execute(status=diet_status, request_user_id=request_user_id)
        elif request_user_id:
            diets = use_case.execute(request_user_id=request_user_id)
        else:
            diets = use_case.execute()
            
        return [self._to_diet_response_dto(diet) for diet in diets]
    
    def list_diets_by_status(self, status: str) -> List[DietResponseDTO]:
        """Lista dietas por estado específico"""
        use_case = ListDietsByStatusUseCase(self.diet_repository)
        diet_status = DietStatus(status)
        diets = use_case.execute(diet_status)
        return [self._to_diet_response_dto(diet) for diet in diets]
    
    def list_diets_pending_liquidation(self) -> List[DietResponseDTO]:
        """Lista dietas pendientes de liquidación"""
        use_case = ListDietsPendingLiquidationUseCase(self.diet_repository)
        diets = use_case.execute()
        return [self._to_diet_response_dto(diet) for diet in diets]
    
    def update_diet(self, diet_id: int, update_dto: DietUpdateDTO) -> Optional[DietResponseDTO]:
        """Actualiza una dieta existente"""
        use_case = UpdateDietUseCase(self.diet_repository)
        
        update_data = {k: v for k, v in update_dto.__dict__.items() if v is not None}
        diet = use_case.execute(diet_id, update_data)
        return self._to_diet_response_dto(diet) if diet else None
    
    def delete_diet(self, diet_id: int) -> bool:
        """Elimina una dieta"""
        use_case = DeleteDietUseCase(
            self.diet_repository,
            self.diet_member_repository,
            self.diet_liquidation_repository
        )
        return use_case.execute(diet_id)
    
    def get_last_advance_number(self) -> int:
        """Obtiene el último número de anticipo utilizado"""
        use_case = GetLastAdvanceNumberUseCase(self.diet_repository)
        return use_case.execute()
    
    def reset_advance_numbers(self) -> bool:
        """Reinicia los números de anticipo"""
        use_case = ResetAdvanceNumbersUseCase(self.diet_repository)
        return use_case.execute()

    # ===== LIQUIDACIONES =====
    
    def create_diet_liquidation(self, create_dto: DietLiquidationCreateDTO) -> DietLiquidationResponseDTO:
        """Crea una liquidación para una dieta"""
        use_case = CreateDietLiquidationUseCase(
            self.diet_repository,
            self.diet_liquidation_repository,
            self.diet_service_repository
        )
        
        liquidation_data = {
            'liquidation_date': create_dto.liquidation_date,
            'breakfast_count_liquidated': create_dto.breakfast_count_liquidated,
            'lunch_count_liquidated': create_dto.lunch_count_liquidated,
            'dinner_count_liquidated': create_dto.dinner_count_liquidated,
            'accommodation_count_liquidated': create_dto.accommodation_count_liquidated,
            'accommodation_payment_method': create_dto.accommodation_payment_method,
            'accommodation_card_id': create_dto.accommodation_card_id
        }
        
        liquidation = use_case.execute(create_dto.diet_id, liquidation_data)
        return self._to_diet_liquidation_response_dto(liquidation)
    
    def get_diet_liquidation(self, liquidation_id: int) -> Optional[DietLiquidationResponseDTO]:
        """Obtiene una liquidación por ID"""
        use_case = GetDietLiquidationUseCase(self.diet_liquidation_repository)
        liquidation = use_case.execute(liquidation_id)
        return self._to_diet_liquidation_response_dto(liquidation) if liquidation else None
    
    def get_liquidation_by_diet(self, diet_id: int) -> Optional[DietLiquidationResponseDTO]:
        """Obtiene la liquidación asociada a una dieta"""
        use_case = GetLiquidationByDietUseCase(self.diet_liquidation_repository)
        liquidation = use_case.execute(diet_id)
        return self._to_diet_liquidation_response_dto(liquidation) if liquidation else None
    
    def list_liquidations_by_date_range(self, start_date: date, end_date: date) -> List[DietLiquidationResponseDTO]:
        """Lista liquidaciones por rango de fechas"""
        use_case = ListLiquidationsByDateRangeUseCase(self.diet_liquidation_repository)
        liquidations = use_case.execute(start_date, end_date)
        return [self._to_diet_liquidation_response_dto(liquidation) for liquidation in liquidations]
    
    def update_diet_liquidation(self, liquidation_id: int, update_dto: DietLiquidationUpdateDTO) -> Optional[DietLiquidationResponseDTO]:
        """Actualiza una liquidación existente"""
        use_case = UpdateDietLiquidationUseCase(self.diet_liquidation_repository)
        
        update_data = {k: v for k, v in update_dto.__dict__.items() if v is not None}
        liquidation = use_case.execute(liquidation_id, update_data)
        return self._to_diet_liquidation_response_dto(liquidation) if liquidation else None
    
    def delete_diet_liquidation(self, liquidation_id: int) -> bool:
        """Elimina una liquidación"""
        use_case = DeleteDietLiquidationUseCase(
            self.diet_liquidation_repository,
            self.diet_repository
        )
        return use_case.execute(liquidation_id)
    
    def get_last_liquidation_number(self) -> int:
        """Obtiene el último número de liquidación utilizado"""
        use_case = GetLastLiquidationNumberUseCase(self.diet_liquidation_repository)
        return use_case.execute()
    
    def reset_liquidation_numbers(self) -> bool:
        """Reinicia los números de liquidación"""
        use_case = ResetLiquidationNumbersUseCase(self.diet_liquidation_repository)
        return use_case.execute()

    # ===== MIEMBROS DE DIETA GRUPAL =====
    
    def add_diet_member(self, create_dto: DietMemberCreateDTO) -> DietMemberResponseDTO:
        """Agrega un miembro a una dieta grupal"""
        use_case = AddDietMemberUseCase(
            self.diet_repository,
            self.diet_member_repository,
            self.request_user_repository
        )
        
        diet_member = use_case.execute(create_dto.diet_id, create_dto.request_user_id)
        return self._to_diet_member_response_dto(diet_member)
    
    def remove_diet_member(self, member_id: int) -> bool:
        """Elimina un miembro de una dieta grupal"""
        use_case = RemoveDietMemberUseCase(self.diet_member_repository)
        return use_case.execute(member_id)
    
    def list_diet_members(self, diet_id: int) -> List[DietMemberResponseDTO]:
        """Lista miembros de una dieta grupal"""
        use_case = ListDietMembersUseCase(self.diet_member_repository)
        members = use_case.execute(diet_id)
        return [self._to_diet_member_response_dto(member) for member in members]

    # ===== OPERACIONES ESPECIALES =====
    
    def calculate_diet_amount(self, calculation_data: Dict[str, Any]) -> DietCalculationDTO:
        """Calcula el monto total de una dieta"""
        use_case = CalculateDietAmountUseCase(self.diet_service_repository)
        
        amount = use_case.execute(
            is_local=calculation_data['is_local'],
            breakfast_count=calculation_data['breakfast_count'],
            lunch_count=calculation_data['lunch_count'],
            dinner_count=calculation_data['dinner_count'],
            accommodation_count=calculation_data['accommodation_count'],
            accommodation_payment_method=calculation_data['accommodation_payment_method']
        )
        
        return DietCalculationDTO(
            is_local=calculation_data['is_local'],
            breakfast_count=calculation_data['breakfast_count'],
            lunch_count=calculation_data['lunch_count'],
            dinner_count=calculation_data['dinner_count'],
            accommodation_count=calculation_data['accommodation_count'],
            accommodation_payment_method=calculation_data['accommodation_payment_method'],
            total_amount=amount
        )
    
    def reset_all_counters(self) -> bool:
        """Reinicia todos los contadores (anticipos y liquidaciones)"""
        use_case = ResetCountersUseCase(
            self.diet_repository,
            self.diet_liquidation_repository
        )
        return use_case.execute()
    
    def get_diet_with_liquidation(self, diet_id: int) -> Optional[DietWithLiquidationDTO]:
        """Obtiene una dieta con su liquidación (si existe)"""
        diet = self.get_diet(diet_id)
        if not diet:
            return None
            
        liquidation = self.get_liquidation_by_diet(diet_id)
        return DietWithLiquidationDTO(diet=diet, liquidation=liquidation)
    
    def get_counters_info(self) -> DietCounterDTO:
        """Obtiene información de los contadores"""
        last_advance = self.get_last_advance_number()
        last_liquidation = self.get_last_liquidation_number()
        
        return DietCounterDTO(
            total_advance_number=last_advance,
            total_liquidation_number=last_liquidation
        )

    # ===== MÉTODOS DE CONVERSIÓN =====
    
    def _to_diet_service_response_dto(self, diet_service: DietService) -> DietServiceResponseDTO:
        return DietServiceResponseDTO(
            id=diet_service.id,                                                                                         # type: ignore
            is_local=diet_service.is_local,
            breakfast_price=diet_service.breakfast_price,
            lunch_price=diet_service.lunch_price,
            dinner_price=diet_service.dinner_price,
            accommodation_cash_price=diet_service.accommodation_cash_price,
            accommodation_card_price=diet_service.accommodation_card_price
        )
    
    def _to_diet_response_dto(self, diet: Diet) -> DietResponseDTO:
        # Calcular monto total si es necesario
        total_amount = None
        try:
            calculation_data = {
                'is_local': diet.is_local,
                'breakfast_count': diet.breakfast_count,
                'lunch_count': diet.lunch_count,
                'dinner_count': diet.dinner_count,
                'accommodation_count': diet.accommodation_count,
                'accommodation_payment_method': diet.accommodation_payment_method.value
            }
            calculation_dto = self.calculate_diet_amount(calculation_data)
            total_amount = calculation_dto.total_amount
        except Exception:
            total_amount = Decimal('0')
        
        return DietResponseDTO(
            id=diet.id,                                                                                                     # type: ignore
            is_local=diet.is_local,
            start_date=diet.start_date,
            end_date=diet.end_date,
            description=diet.description,
            advance_number=diet.advance_number,
            is_group=diet.is_group,
            status=diet.status.value,
            request_user_id=diet.request_user_id,
            diet_service_id=diet.diet_service_id,
            breakfast_count=diet.breakfast_count,
            lunch_count=diet.lunch_count,
            dinner_count=diet.dinner_count,
            accommodation_count=diet.accommodation_count,
            accommodation_payment_method=diet.accommodation_payment_method.value,
            accommodation_card_id=diet.accommodation_card_id,
            created_at=diet.created_at,
            total_amount=total_amount
        )
    
    def _to_diet_liquidation_response_dto(self, liquidation: DietLiquidation) -> DietLiquidationResponseDTO:
        # Calcular monto liquidado
        liquidated_amount = None
        try:
            diet_service = self.diet_service_repository.get_by_id(liquidation.diet_service_id)
            if diet_service:
                if liquidation.accommodation_payment_method.value == "CASH":
                    accommodation_price = diet_service.accommodation_cash_price
                else:
                    accommodation_price = diet_service.accommodation_card_price
                
                liquidated_amount = (
                    Decimal(diet_service.breakfast_price) * liquidation.breakfast_count_liquidated +
                    Decimal(diet_service.lunch_price) * liquidation.lunch_count_liquidated +
                    Decimal(diet_service.dinner_price) * liquidation.dinner_count_liquidated +
                    Decimal(accommodation_price) * liquidation.accommodation_count_liquidated
                )
        except Exception:
            liquidated_amount = Decimal('0')
        
        return DietLiquidationResponseDTO(
            id=liquidation.id,                                                                                           # type: ignore
            diet_id=liquidation.diet_id,
            liquidation_number=liquidation.liquidation_number,
            liquidation_date=liquidation.liquidation_date,
            breakfast_count_liquidated=liquidation.breakfast_count_liquidated,
            lunch_count_liquidated=liquidation.lunch_count_liquidated,
            dinner_count_liquidated=liquidation.dinner_count_liquidated,
            accommodation_count_liquidated=liquidation.accommodation_count_liquidated,
            accommodation_payment_method=liquidation.accommodation_payment_method.value,
            diet_service_id=liquidation.diet_service_id,
            accommodation_card_id=liquidation.accommodation_card_id,
            liquidated_amount=liquidated_amount
        )
    
    def _to_diet_member_response_dto(self, diet_member: DietMember) -> DietMemberResponseDTO:
        # Obtener información del solicitante
        request_user = self.request_user_repository.get_by_id(diet_member.request_user_id)
        request_user_name = request_user.fullname if request_user else "Desconocido"
        request_user_ci = request_user.ci if request_user else "N/A"
        
        return DietMemberResponseDTO(
            id=diet_member.id,                                                                                          # type: ignore
            diet_id=diet_member.diet_id,
            request_user_id=diet_member.request_user_id,
            request_user_name=request_user_name,
            request_user_ci=request_user_ci
        )