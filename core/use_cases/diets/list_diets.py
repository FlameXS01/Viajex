from typing import List
from core.entities.diet import Diet, DietStatus
from core.repositories.diet_repository import DietRepository

class ListDietsUseCase:
    """Caso de uso para listar dietas con filtros opcionales"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(
        self, 
        status: DietStatus = None, 
        request_user_id: int = None
    ) -> List[Diet]:
        if status:
            return self.diet_repository.list_by_status(status)
        elif request_user_id:
            return self.diet_repository.list_by_request_user(request_user_id)
        else:
            # En una implementación real, podrías tener un método list_all
            return self.diet_repository.list_by_status(DietStatus.REQUESTED) + \
                   self.diet_repository.list_by_status(DietStatus.LIQUIDATED)