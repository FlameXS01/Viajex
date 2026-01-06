from datetime import datetime, timedelta, date
from core.entities.diet import DietStatus
from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_repository import DietRepository
from core.repositories.diet_liquidation_repository import DietLiquidationRepository
from core.repositories.diet_service_repository import DietServiceRepository

class CreateDietLiquidationUseCase:
    """Caso de uso para liquidar una dieta existente"""
    
    def __init__(
        self,
        diet_repository: DietRepository,
        diet_liquidation_repository: DietLiquidationRepository,
        diet_service_repository: DietServiceRepository
    ):
        self.diet_repository = diet_repository
        self.diet_liquidation_repository = diet_liquidation_repository
        self.diet_service_repository = diet_service_repository
    
    def execute(self, diet_id: int, liquidation_data: dict) -> DietLiquidation:
        # Obtener la dieta original
        diet = self.diet_repository.get_by_id(diet_id)
        if not diet:
            raise ValueError("La dieta no existe")
        

        liquidation_date = liquidation_data['liquidation_date']
        max_liquidation_date = diet.end_date + timedelta(days=3)
        
        
        # Validar que las cantidades liquidadas no excedan las solicitadas
        if (liquidation_data['breakfast_count_liquidated'] > diet.breakfast_count or
            liquidation_data['lunch_count_liquidated'] > diet.lunch_count or
            liquidation_data['dinner_count_liquidated'] > diet.dinner_count or
            liquidation_data['accommodation_count_liquidated'] > diet.accommodation_count):
            raise ValueError("Las cantidades liquidadas no pueden exceder las solicitadas")
        
        # Obtener el próximo número de liquidación
        last_liquidation_number = self.diet_liquidation_repository.get_last_liquidation_number()
        liquidation_number = last_liquidation_number + 1
        
        # Crear la liquidación
        diet_liquidation = DietLiquidation(
            diet_id=diet_id,
            liquidation_number=liquidation_number,
            liquidation_date=liquidation_date,
            breakfast_count_liquidated=liquidation_data['breakfast_count_liquidated'],
            lunch_count_liquidated=liquidation_data['lunch_count_liquidated'],
            dinner_count_liquidated=liquidation_data['dinner_count_liquidated'],
            accommodation_count_liquidated=liquidation_data['accommodation_count_liquidated'],
            accommodation_payment_method=liquidation_data['accommodation_payment_method'].upper(),
            diet_service_id=diet.diet_service_id,
            accommodation_card_id=liquidation_data.get('accommodation_card_id'),
            total_pay=liquidation_data.get('total_pay') if liquidation_data.get('total_pay') else 0
        )
        
        # Crear la liquidación o editarla
        if self.diet_repository.get_by_id(diet_liquidation.diet_id).status == 'liquidated':
            liquidation = self.diet_liquidation_repository.update(diet_liquidation)
        else:
            liquidation = self.diet_liquidation_repository.create(diet_liquidation)
            # Actualizar solo el Status solamente ya que se necesita tener control de lo q se liquido y de lo q se solicito
            self.diet_repository.update_status(diet.id,  DietStatus.LIQUIDATED.value)  # type: ignore
        
        return liquidation