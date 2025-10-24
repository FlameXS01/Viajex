from typing import List
from core.entities.dieta_base import DietaBase
from core.repositories.dieta_anticipo_repository import DietaAnticipoRepository
from core.repositories.dieta_liquidacion_repository import DietaLiquidacionRepository

class ListarDietasUseCase:
    def __init__(self, 
                 dieta_anticipo_repository: DietaAnticipoRepository,
                 dieta_liquidacion_repository: DietaLiquidacionRepository):
        self.dieta_anticipo_repository = dieta_anticipo_repository
        self.dieta_liquidacion_repository = dieta_liquidacion_repository

    def execute(self) -> list[DietaBase]:
        """
        Lista todas las dietas (anticipos y liquidaciones)
        """
        anticipos = self.dieta_anticipo_repository.get_all()
        liquidaciones = self.dieta_liquidacion_repository.get_all()
        total = anticipos + liquidaciones
        return total            # type: ignore