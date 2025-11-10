# application/dtos/diet_dtos.py
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

@dataclass
class DietServiceResponseDTO:
    """DTO para respuesta de servicios de dieta"""
    id: int
    is_local: bool
    breakfast_price: float
    lunch_price: float
    dinner_price: float
    accommodation_cash_price: float
    accommodation_card_price: float

@dataclass
class DietServiceCreateDTO:
    """DTO para crear servicios de dieta"""
    is_local: bool
    breakfast_price: float
    lunch_price: float
    dinner_price: float
    accommodation_cash_price: float
    accommodation_card_price: float

@dataclass
class DietServiceUpdateDTO:
    """DTO para actualizar servicios de dieta"""
    breakfast_price: Optional[float] = None
    lunch_price: Optional[float] = None
    dinner_price: Optional[float] = None
    accommodation_cash_price: Optional[float] = None
    accommodation_card_price: Optional[float] = None

@dataclass
class DietCreateDTO:
    """DTO para crear un anticipo de dieta"""
    is_local: bool
    start_date: date
    end_date: date
    description: str
    is_group: bool
    request_user_id: int
    diet_service_id: int
    breakfast_count: int
    lunch_count: int
    dinner_count: int
    accommodation_count: int
    accommodation_payment_method: str
    accommodation_card_id: Optional[int] = None

@dataclass
class DietUpdateDTO:
    """DTO para actualizar un anticipo de dieta"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    breakfast_count: Optional[int] = None
    lunch_count: Optional[int] = None
    dinner_count: Optional[int] = None
    accommodation_count: Optional[int] = None
    accommodation_payment_method: Optional[str] = None
    accommodation_card_id: Optional[int] = None

@dataclass
class DietResponseDTO:
    """DTO para respuesta de dieta (anticipo)"""
    id: int
    is_local: bool
    start_date: date
    end_date: date
    description: str
    advance_number: int
    is_group: bool
    status: str
    request_user_id: int
    diet_service_id: int
    breakfast_count: int
    lunch_count: int
    dinner_count: int
    accommodation_count: int
    accommodation_payment_method: str
    accommodation_card_id: Optional[int]
    created_at: datetime
    total_amount: Optional[Decimal] = None

@dataclass
class DietLiquidationCreateDTO:
    """DTO para crear una liquidación"""
    diet_id: int
    liquidation_date: datetime
    breakfast_count_liquidated: int
    lunch_count_liquidated: int
    dinner_count_liquidated: int
    accommodation_count_liquidated: int
    accommodation_payment_method: str
    diet_service_id: int
    accommodation_card_id: Optional[int] = None

@dataclass
class DietLiquidationUpdateDTO:
    """DTO para actualizar una liquidación"""
    breakfast_count_liquidated: Optional[int] = None
    lunch_count_liquidated: Optional[int] = None
    dinner_count_liquidated: Optional[int] = None
    accommodation_count_liquidated: Optional[int] = None
    accommodation_payment_method: Optional[str] = None
    accommodation_card_id: Optional[int] = None

@dataclass
class DietLiquidationResponseDTO:
    """DTO para respuesta de liquidación"""
    id: int
    diet_id: int
    liquidation_number: int
    liquidation_date: datetime
    breakfast_count_liquidated: int
    lunch_count_liquidated: int
    dinner_count_liquidated: int
    accommodation_count_liquidated: int
    accommodation_payment_method: str
    diet_service_id: int
    accommodation_card_id: Optional[int]
    liquidated_amount: Optional[Decimal] = None

@dataclass
class DietMemberCreateDTO:
    """DTO para agregar miembro a dieta grupal"""
    diet_id: int
    request_user_id: int

@dataclass
class DietMemberResponseDTO:
    """DTO para respuesta de miembro de dieta"""
    id: int
    diet_id: int
    request_user_id: int
    request_user_name: str
    request_user_ci: str

@dataclass
class DietCalculationDTO:
    """DTO para cálculo de montos de dieta"""
    is_local: bool
    breakfast_count: int
    lunch_count: int
    dinner_count: int
    accommodation_count: int
    accommodation_payment_method: str
    total_amount: Decimal

@dataclass
class DietWithLiquidationDTO:
    """DTO para dieta con su liquidación"""
    diet: DietResponseDTO
    liquidation: Optional[DietLiquidationResponseDTO] = None

@dataclass
class DietCounterDTO:
    """DTO para contadores de dietas"""
    total_advance_number: int
    total_liquidation_number: int