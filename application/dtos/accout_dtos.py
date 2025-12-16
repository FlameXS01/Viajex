from dataclasses import dataclass
from typing import Optional

@dataclass
class AccountCreateDTO:
    """DTO para creación de cuentas"""
    account: str
    description: Optional[str] = None

@dataclass
class AccountUpdateDTO:
    """DTO para actualización de cuentas"""
    account: Optional[str] = None
    description: Optional[str] = None

@dataclass
class AccountResponseDTO:
    """DTO para respuesta de cuentas"""
    id: int
    account: str
    description: Optional[str] = None