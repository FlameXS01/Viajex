from core.repositories.diet_service_repository import DietServiceRepository

class CalculateDietAmountUseCase:
    """Caso de uso para calcular el monto total de una dieta"""
    
    def __init__(self, diet_service_repository: DietServiceRepository):
        self.diet_service_repository = diet_service_repository
    
    def execute(
        self,
        is_local: bool,
        breakfast_count: int,
        lunch_count: int,
        dinner_count: int,
        accommodation_count: int,
        accommodation_payment_method: str
    ) -> float:
        # Obtener los precios según localidad
        diet_service = self.diet_service_repository.get_by_local(is_local)
        if not diet_service:
            raise ValueError("No se encontraron precios para la localidad especificada")
        
        # Calcular montos
        breakfast_total = float(diet_service.breakfast_price) * breakfast_count
        lunch_total = float(diet_service.lunch_price) * lunch_count
        dinner_total = float(diet_service.dinner_price) * dinner_count
        
        # Calcular alojamiento según método de pago
        if accommodation_payment_method == "CASH":
            accommodation_total = float(diet_service.accommodation_cash_price) * accommodation_count
        else:
            accommodation_total = float(diet_service.accommodation_card_price) * accommodation_count
        
        total_amount = breakfast_total + lunch_total + dinner_total + accommodation_total
        
        return total_amount