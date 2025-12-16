from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from core.entities.diet_liquidation import DietLiquidation
from core.entities.enums import DietStatus

class DietLiquidationRepository(ABC):
    """

    Interfaz para el repositorio de liquidaciones de dieta.
    Define los contratos para las operaciones CRUD y consultas específicas.

    """
    
    @abstractmethod
    def create(self, diet_liquidation: DietLiquidation) -> DietLiquidation:
        """
        
        Crea una nueva liquidación de dieta
        
        """
        pass
    
    @abstractmethod
    def get_by_id(self, liquidation_id: int) -> Optional[DietLiquidation]:
        """
        
        Obtiene una liquidación por ID
        
        """
        pass
    
    @abstractmethod
    def get_by_liquidation_number(self, liquidation_number: int) -> Optional[DietLiquidation]:
        """
        
        Obtiene una liquidación por número de liquidación
        
        """
        pass
    
    @abstractmethod
    def get_by_diet_id(self, diet_id: int) -> Optional[DietLiquidation]:
        """
        
        Obtiene la liquidación asociada a una dieta
        
        """
        pass
    
    @abstractmethod
    def list_by_date_range(self, start_date: date, end_date: date) -> List[DietLiquidation]:
        """
        
        Lista liquidaciones por rango de fechas
        
        """
        pass
    
    @abstractmethod
    def list_all(self) -> List[DietLiquidation]:
        """
        
        Lista todas las liquidaciones
        
        """
        pass


    
    @abstractmethod
    def update(self, diet_liquidation: DietLiquidation) -> DietLiquidation:
        """
        
        Actualiza una liquidación existente
        
        """
        pass
    
    @abstractmethod
    def delete(self, liquidation_id: int) -> bool:
        """
        
        Elimina una liquidación
        
        """
        pass
    
    @abstractmethod
    def get_last_liquidation_number(self) -> int:
        """
        
        Obtiene el último número de liquidación utilizado
        
        """
        pass
    
    