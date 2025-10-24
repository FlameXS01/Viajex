from abc import ABC
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from .enums import MetodoPagoHospedaje, TipoServicio
from .opciones import OpcionBase, OpcionLocal, OpcionForeign

@dataclass
class DietaBase(ABC):
    en_territorio: bool
    creada_at: str                                                              # Formato "dd-mm-yy"
    descripcion: str
    es_grupal: bool
    id: Optional[int] = None
    cantidad_personas: int = 1
    opciones: List[OpcionBase] = field(default_factory=list)
    
    def __post_init__(self):
        self._validar_cantidad_personas()
        self._inicializar_opciones_por_territorio()
    
    def _validar_cantidad_personas(self) -> None:
        """Valida las reglas de cantidad de personas"""
        if self.es_grupal:
            if self.cantidad_personas is None or self.cantidad_personas <= 1:
                raise ValueError("Para dietas grupales, cantidad_personas es obligatorio y mayor a 1")
        else:
            if self.cantidad_personas is not None:
                raise ValueError("Para dietas individuales, cantidad_personas debe ser None")
    
    def _inicializar_opciones_por_territorio(self) -> None:
        """Inicializa las opciones controladas según el territorio"""
        pass
    
    def agregar_opcion(self, tipo_servicio: TipoServicio, metodo_pago: Optional[MetodoPagoHospedaje] = None) -> None:
        """Agrega una opción controlada según el territorio"""
        if self.en_territorio:
            opcion = OpcionLocal(tipo_servicio, metodo_pago)
        else:
            opcion = OpcionForeign(tipo_servicio, metodo_pago)
        
        self.opciones.append(opcion)
    
    def obtener_detalle_precios(self) -> List[dict]:
        """Devuelve el detalle de precios por servicio"""
        detalle = []
        for opcion in self.opciones:
            detalle.append({
                'servicio': opcion.tipo_servicio.value,
                'precio_unitario': opcion.calcular_precio(),
                'metodo_pago': opcion.metodo_pago.value if opcion.metodo_pago else 'N/A',
                'territorio': 'local' if self.en_territorio else 'foreign'
            })
        return detalle
    
    def tiene_servicio(self, tipo_servicio: TipoServicio) -> bool:
        """Verifica si la dieta incluye un servicio específico"""
        return any(opcion.tipo_servicio == tipo_servicio for opcion in self.opciones)
    
    @property
    def total_personas(self) -> int:
        """Devuelve la cantidad total de personas"""
        return self.cantidad_personas if self.es_grupal else 1