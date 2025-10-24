from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.dieta_base import DietaBase

class DietaBaseRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, dieta_id: int) -> Optional[DietaBase]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[DietaBase]:
        pass
    
    @abstractmethod
    def create(self, dieta: DietaBase) -> DietaBase:
        pass
    
    @abstractmethod
    def update(self, dieta: DietaBase) -> DietaBase:
        pass
    
    @abstractmethod
    def delete(self, dieta_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_territorio(self, en_territorio: bool) -> List[DietaBase]:
        pass
    
    @abstractmethod
    def get_by_tipo_grupal(self, es_grupal: bool) -> List[DietaBase]:
        pass
    
    @abstractmethod
    def get_by_fecha(self, fecha: str) -> List[DietaBase]:
        pass