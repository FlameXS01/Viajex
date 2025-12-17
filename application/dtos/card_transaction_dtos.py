from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any


@dataclass
class CreateCardTransactionRequest:
    """
    DTO para crear una nueva transacción de tarjeta.
    
    Campos:
        card_id: ID de la tarjeta afectada
        transaction_type: Tipo de transacción (RECHARGE, DIET_ADVANCE, etc.)
        amount: Monto de la transacción (positivo para créditos, negativo para débitos)
        description: Descripción opcional
        reference_id: ID de la entidad relacionada (dieta, liquidación, etc.)
        reference_type: Tipo de referencia
    """
    card_id: int
    transaction_type: str
    amount: Decimal
    description: Optional[str] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None


@dataclass
class CardTransactionResponse:
    """
    DTO para respuesta de transacción de tarjeta.
    
    Incluye todos los campos de auditoría y trazabilidad.
    """
    id: int
    card_id: int
    transaction_type: str
    amount: Decimal
    previous_balance: Decimal
    new_balance: Decimal
    operation_date: datetime
    recorded_at: datetime
    description: Optional[str] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None

    @property
    def is_credit(self) -> bool:
        return self.amount > 0

    @property
    def is_debit(self) -> bool:
        return self.amount < 0


@dataclass
class GetCardTransactionsRequest:
    """
    DTO para solicitar transacciones con filtros.
    """
    card_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transaction_type: Optional[str] = None
    reference_type: Optional[str] = None


@dataclass
class GetCardTransactionsResponse:
    """
    DTO para respuesta con lista de transacciones.
    """
    success: bool
    transactions: List[CardTransactionResponse]
    total_count: int
    total_credits: Decimal
    total_debits: Decimal
    net_movement: Decimal
    message: Optional[str] = None


@dataclass
class GetCardBalanceAtDateRequest:
    """
    DTO para consultar balance en una fecha específica.
    """
    card_id: int
    target_date: datetime


@dataclass
class GetCardBalanceAtDateResponse:
    """
    DTO para respuesta de balance histórico.
    """
    success: bool
    card_id: int
    target_date: datetime
    balance_at_date: Decimal
    message: Optional[str] = None


@dataclass
class GetCardMonthlySummaryRequest:
    """
    DTO para solicitar resumen mensual.
    """
    card_id: int
    year: int
    month: Optional[int] = None


@dataclass
class MonthlySummary:
    """
    DTO para resumen mensual individual.
    """
    month: int
    opening_balance: Decimal
    closing_balance: Decimal
    total_credits: Decimal
    total_debits: Decimal
    transaction_count: int
    net_movement: Decimal


@dataclass
class GetCardMonthlySummaryResponse:
    """
    DTO para respuesta de resumen mensual/anual.
    """
    success: bool
    card_id: int
    year: int
    monthly_summaries: List[MonthlySummary]
    annual_totals: Dict[str, Any]
    message: Optional[str] = None


@dataclass
class CardBalanceHistoryRequest:
    """
    DTO para solicitar historial de balances.
    """
    card_id: int
    start_date: date
    end_date: date


@dataclass
class CardBalanceHistoryResponse:
    """
    DTO para respuesta de historial de balances.
    """
    success: bool
    card_id: int
    period: Dict[str, date]
    daily_balances: List[Dict[str, Any]]
    opening_balance: Decimal
    closing_balance: Decimal
    total_movement: Decimal
    message: Optional[str] = None


@dataclass
class ExportTransactionsRequest:
    """
    DTO para exportar transacciones.
    """
    card_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    export_format: str = "csv"  # csv, excel, json
    include_summary: bool = True


@dataclass
class ExportTransactionsResponse:
    """
    DTO para respuesta de exportación.
    """
    success: bool
    file_path: str
    file_size: int
    transaction_count: int
    message: Optional[str] = None