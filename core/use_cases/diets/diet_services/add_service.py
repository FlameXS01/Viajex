from typing import Optional
from core.entities.diet_service import DietService
from core.repositories.diet_service_repository import DietServiceRepository

class AddDietServiceUseCase:
    """Caso de uso para agregar un nuevo servicio de dieta"""
    
    def __init__(self, diet_service_repository: DietServiceRepository):
        self.diet_service_repository = diet_service_repository
    
    def execute(self, is_local: bool, breakfast_price: float, lunch_price: float, 
                dinner_price: float, accommodation_cash_price: float, 
                accommodation_card_price: float) -> Optional[DietService]:
        
        # Validaciones de precios no negativos
        if breakfast_price < 0:
            raise ValueError("El precio del desayuno no puede ser negativo")
        
        if lunch_price < 0:
            raise ValueError("El precio del almuerzo no puede ser negativo")
            
        if dinner_price < 0:
            raise ValueError("El precio de la comida no puede ser negativo")
            
        if accommodation_cash_price < 0:
            raise ValueError("El precio de alojamiento en efectivo no puede ser negativo")
            
        if accommodation_card_price < 0:
            raise ValueError("El precio de alojamiento con tarjeta no puede ser negativo")
        
        service = self.diet_service_repository.get_by_local(is_local)
        if service: 
            raise ValueError("Ya el servicio existe, modifique el existente")
        
        # Crear nueva entidad DietService con los parámetros proporcionados
        new_service = DietService(
            is_local=is_local,
            breakfast_price=breakfast_price,
            lunch_price=lunch_price,
            dinner_price=dinner_price,
            accommodation_cash_price=accommodation_cash_price,
            accommodation_card_price=accommodation_card_price
        )
        
        # Guardar en el repositorio
        return self.diet_service_repository.create(new_service)