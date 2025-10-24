from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.dieta import DietaLiquidacion
from core.entities.enums import EstadoLiquidacion

class DietaLiquidacionRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, liquidacion_id: int) -> Optional[DietaLiquidacion]:
        pass
    
    @abstractmethod
    def get_by_numero_liquidacion(self, numero_liquidacion: str) -> Optional[DietaLiquidacion]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[DietaLiquidacion]:
        pass
    
    @abstractmethod
    def create(self, liquidacion: DietaLiquidacion) -> DietaLiquidacion:
        pass
    
    @abstractmethod
    def update(self, liquidacion: DietaLiquidacion) -> DietaLiquidacion:
        pass
    
    @abstractmethod
    def delete(self, liquidacion_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_estado(self, estado: EstadoLiquidacion) -> List[DietaLiquidacion]:
        pass
    
    @abstractmethod
    def get_pendientes(self) -> List[DietaLiquidacion]:
        pass
    
    @abstractmethod
    def get_liquidadas(self) -> List[DietaLiquidacion]:
        pass
    
    @abstractmethod
    def liquidar_liquidacion(self, liquidacion_id: int, numero_liquidacion: str) -> bool:
        pass
    
    @abstractmethod
    def get_liquidaciones_para_liquidar(self) -> List[DietaLiquidacion]:
        pass
    
    @abstractmethod
    def get_by_anticipo_id(self, anticipo_id: int) -> Optional[DietaLiquidacion]:
        pass