from typing import Optional
from dataclasses import dataclass
from .dieta_base import DietaBase
from .enums import EstadoAnticipo, EstadoLiquidacion

@dataclass
class DietaAnticipo(DietaBase):
    
    estado: EstadoAnticipo = EstadoAnticipo.PENDIENTE
    numero_anticipo: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self._validar_estado_inicial()
    
    def _validar_estado_inicial(self) -> None:
        """Valida el estado inicial del anticipo"""
        if self.estado == EstadoAnticipo.LIQUIDADA and not self.numero_anticipo:
            raise ValueError("Un anticipo liquidado debe tener número de anticipo")
    
    def liquidar(self, numero_anticipo: str) -> None:
        """Liquida el anticipo"""
        if self.estado == EstadoAnticipo.LIQUIDADA:
            raise ValueError("El anticipo ya está liquidado")
        
        self.numero_anticipo = numero_anticipo
        self.estado = EstadoAnticipo.LIQUIDADA
    
    @property
    def puede_liquidar(self) -> bool:
        """Indica si el anticipo puede ser liquidado"""
        return self.estado == EstadoAnticipo.PENDIENTE

@dataclass
class DietaLiquidacion(DietaBase):
    estado: EstadoLiquidacion = EstadoLiquidacion.PENDIENTE
    numero_liquidacion: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self._validar_estado_inicial()
    
    def _validar_estado_inicial(self) -> None:
        """Valida el estado inicial de la liquidación"""
        if self.estado == EstadoLiquidacion.LIQUIDADA and not self.numero_liquidacion:
            raise ValueError("Una liquidación liquidada debe tener número de liquidación")
    
    def liquidar(self, numero_liquidacion: str) -> None:
        """Liquida la liquidación"""
        if self.estado == EstadoLiquidacion.LIQUIDADA:
            raise ValueError("La liquidación ya está liquidada")
        
        self.numero_liquidacion = numero_liquidacion
        self.estado = EstadoLiquidacion.LIQUIDADA
    
    @property
    def puede_liquidar(self) -> bool:
        """Indica si la liquidación puede ser liquidada"""
        return self.estado == EstadoLiquidacion.PENDIENTE