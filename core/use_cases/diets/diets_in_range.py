import datetime
from typing import List
from core.entities.diet import Diet, DietStatus
from core.repositories.diet_repository import DietRepository
from datetime import date

class DietsInRangeUseCase:
    """Caso de uso para listar dietas con filtros opcionales"""
    
    def __init__(self, diet_repository: DietRepository):
        self.diet_repository = diet_repository
    
    def execute(self, date_in: date, date_end: date) -> list[Diet]:
        return self.diet_repository.list_by_date_range(start_date = date_in, end_date= date_end)