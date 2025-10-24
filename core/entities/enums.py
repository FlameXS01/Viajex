from enum import Enum
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

class EstadoAnticipo(Enum):
    PENDIENTE = "pendiente"
    LIQUIDADA = "liquidada"

class EstadoLiquidacion(Enum):
    PENDIENTE = "pendiente"
    LIQUIDADA = "liquidada"

class MetodoPagoHospedaje(Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"

class TipoServicio(Enum):
    DESAYUNO = "desayuno"
    ALMUERZO = "almuerzo"
    COMIDA = "comida"
    HOSPEDAJE = "hospedaje"