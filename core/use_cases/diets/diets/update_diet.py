from core.entities.diet import Diet, DietStatus
from core.repositories.diet_repository import DietRepository

class UpdateDietUseCase:
    """Caso de uso para actualizar una dieta existente"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self, diet_id: int, update_data: dict) -> Diet:
        diet = self.diet_repository.get_by_id(diet_id)
        if not diet:
            raise ValueError("La dieta no existe")
        
        # Validar que no esté liquidada
        if diet.status == DietStatus.LIQUIDATED:
            raise ValueError("No se puede modificar una dieta liquidada")
        
        # Actualizar campos permitidos
        for field, value in update_data.items():
            if hasattr(diet, field) and field not in ['id', 'advance_number']:
                setattr(diet, field, value)
        
        return self.diet_repository.update(diet)