from core.repositories.diet_repository import DietRepository

class GetLastAdvanceNumberUseCase:
    """Caso de uso para obtener el último número de anticipo utilizado"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self) -> int:
        return self.diet_repository.get_last_advance_number()