from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.dieta import DietaAnticipo
from core.entities.enums import EstadoAnticipo

class DietaAnticipoRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, anticipo_id: int) -> Optional[DietaAnticipo]:
        pass
    
    @abstractmethod
    def get_by_numero_anticipo(self, numero_anticipo: str) -> Optional[DietaAnticipo]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[DietaAnticipo]:
        pass
    
    @abstractmethod
    def create(self, anticipo: DietaAnticipo) -> DietaAnticipo:
        pass
    
    @abstractmethod
    def update(self, anticipo: DietaAnticipo) -> DietaAnticipo:
        pass
    
    @abstractmethod
    def delete(self, anticipo_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_estado(self, estado: EstadoAnticipo) -> List[DietaAnticipo]:
        pass
    
    @abstractmethod
    def get_pendientes(self) -> List[DietaAnticipo]:
        pass
    
    @abstractmethod
    def get_liquidadas(self) -> List[DietaAnticipo]:
        pass
    
    @abstractmethod
    def liquidar_anticipo(self, anticipo_id: int, numero_anticipo: str) -> bool:
        pass
    
    @abstractmethod
    def get_anticipos_para_liquidar(self) -> List[DietaAnticipo]:
        pass