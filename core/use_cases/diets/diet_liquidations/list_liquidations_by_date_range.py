from typing import List
from datetime import date
from core.entities.diet_liquidation import DietLiquidation
from core.repositories.diet_liquidation_repository import DietLiquidationRepository

class ListLiquidationsByDateRangeUseCase:
    """Caso de uso para listar liquidaciones por rango de fechas"""
    
    def __init__(self, diet_liquidation_repository: DietLiquidationRepository):
        self.diet_liquidation_repository = diet_liquidation_repository
    
    def execute(self, start_date: date, end_date: date) -> List[DietLiquidation]:
        return self.diet_liquidation_repository.list_by_date_range(start_date, end_date)