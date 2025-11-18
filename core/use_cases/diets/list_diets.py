from typing import List
from core.entities.diet import Diet, DietStatus
from core.repositories.diet_repository import DietRepository

class ListDietsUseCase:
    """Caso de uso para listar dietas con filtros opcionales"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(
        self, 
        status: str = None, 
        request_user_id: int = None
    ) -> List[Diet]:
        
        if status:
            list = self.diet_repository.list_by_status(status)
            return list
        elif request_user_id is not None:
            return self.diet_repository.list_by_request_user(request_user_id)
        else:
            # Por defecto mostrar ambas
            return self.diet_repository.list_by_status(DietStatus.REQUESTED) + \
                self.diet_repository.list_by_status(DietStatus.LIQUIDATED)