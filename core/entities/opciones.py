# core/entities/opciones_controladas.py
from abc import ABC, abstractmethod
from typing import Optional

from core.entities.value_objects import UserRole
from .enums import TipoServicio, MetodoPagoHospedaje

class OpcionBase(ABC):
    def __init__(self, tipo_servicio: TipoServicio, metodo_pago: Optional[MetodoPagoHospedaje] = MetodoPagoHospedaje.EFECTIVO):
        self.tipo_servicio = tipo_servicio
        self.metodo_pago = metodo_pago
    
    @abstractmethod
    def calcular_precio(self) -> float:
        pass
    
    @abstractmethod
    def get_precio_territorio(self) -> float:
        pass
    
    def __str__(self) -> str:
        return f"{self.tipo_servicio.value} - ${self.calcular_precio()}"

class OpcionLocal(OpcionBase):
    def calcular_precio(self) -> float:
        return self.get_precio_territorio()
    
    def get_precio_territorio(self) -> float:
        PRECIOS_LOCAL = {
            TipoServicio.DESAYUNO: 200.0,
            TipoServicio.ALMUERZO: 200.0,
            TipoServicio.COMIDA: 200.0,
            TipoServicio.HOSPEDAJE: 200.0
        }
        return PRECIOS_LOCAL.get(self.tipo_servicio, 0.0)

class OpcionForeign(OpcionBase):
    def calcular_precio(self) -> float:
        return self.get_precio_territorio()
    
    def get_precio_territorio(self) -> float:
        PRECIOS_FOREIGN = {
            TipoServicio.DESAYUNO: 300.0,
            TipoServicio.ALMUERZO: 300.0,
            TipoServicio.COMIDA: 300.0,
            TipoServicio.HOSPEDAJE: 300.0
        }
        return PRECIOS_FOREIGN.get(self.tipo_servicio, 0.0)