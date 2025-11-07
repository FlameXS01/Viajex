from core.repositories.diet_repository import DietRepository

class ResetAdvanceNumbersUseCase:
    """Caso de uso específico para reiniciar números de anticipo"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self) -> bool:
        return self.diet_repository.reset_advance_numbers()