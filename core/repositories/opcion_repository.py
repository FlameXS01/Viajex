from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.opciones import OpcionBase, OpcionLocal, OpcionForeign
from core.entities.enums import TipoServicio, MetodoPagoHospedaje

class OpcionRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, opcion_id: int) -> Optional[OpcionBase]:
        pass
    
    @abstractmethod
    def get_by_dieta_id(self, dieta_id: int) -> List[OpcionBase]:
        pass
    
    @abstractmethod
    def get_by_tipo_servicio(self, tipo_servicio: TipoServicio) -> List[OpcionBase]:
        pass
    
    @abstractmethod
    def create(self, opcion: OpcionBase, dieta_id: int) -> OpcionBase:
        pass
    
    @abstractmethod
    def update(self, opcion: OpcionBase) -> OpcionBase:
        pass
    
    @abstractmethod
    def delete(self, opcion_id: int) -> bool:
        pass
    
    @abstractmethod
    def delete_by_dieta_id(self, dieta_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_precios_por_servicio(self, tipo_servicio: TipoServicio) -> dict:
        pass