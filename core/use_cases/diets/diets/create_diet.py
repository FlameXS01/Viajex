from typing import Optional
from core.entities.diet import Diet, DietStatus
from core.repositories.diet_repository import DietRepository
from core.repositories.diet_service_repository import DietServiceRepository
from core.repositories.request_user_repository import RequestUserRepository

class CreateDietUseCase:
    """
    
    Caso de uso para crear un nuevo anticipo de dieta
    
    """
    def __init__(
        self, 
        diet_repository: DietRepository,
        diet_service_repository: DietServiceRepository,
        request_user_repository: RequestUserRepository,
    ):
        self.diet_repository = diet_repository
        self.diet_service_repository = diet_service_repository
        self.request_user_repository = request_user_repository


    def execute(self, diet_data: dict) -> Diet:
        # request_user_id debe ser un solo ID, no una lista
        request_user = self.request_user_repository.get_by_id(diet_data['request_user_id'])
        if not request_user:
            raise ValueError("El solicitante no existe")
            
        # Validar que el servicio de dieta existe
        diet_service = self.diet_service_repository.get_by_local(diet_data['is_local'])
        if not diet_service:
            raise ValueError("El servicio de dieta no existe")
            
        # Obtener el próximo número de anticipo
        last_advance_number = self.diet_repository.get_last_advance_number()
        advance_number = last_advance_number + 1
        
        # Crear UNA sola dieta
        diet = Diet(
            is_local=diet_data['is_local'],
            start_date=diet_data['start_date'],
            end_date=diet_data['end_date'],
            description=diet_data['description'],
            advance_number=advance_number,
            is_group=diet_data['is_group'],
            status=DietStatus.REQUESTED,
            request_user_id=diet_data['request_user_id'],  
            diet_service_id=diet_service.id,
            breakfast_count=diet_data['breakfast_count'],
            lunch_count=diet_data['lunch_count'],
            dinner_count=diet_data['dinner_count'],
            accommodation_count=diet_data['accommodation_count'],
            accommodation_payment_method=diet_data['accommodation_payment_method'],
            accommodation_card_id=diet_data.get('accommodation_card_id')
        )
        
        created_diet = self.diet_repository.create(diet)
        return created_diet
    