from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.account import Account

class AccountRepository(ABC):

    @abstractmethod
    def save(self, account: Account) -> Account:
        """Guarda una nueva cuenta o actualiza una existente"""
        pass

    @abstractmethod
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Obtiene una cuenta por su ID"""
        pass

    @abstractmethod
    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Obtiene una cuenta por su número de cuenta"""
        pass

    @abstractmethod
    def get_all(self) -> List[Account]:
        """Obtiene todas las cuentas del sistema"""
        pass

    @abstractmethod
    def update(self, account: Account) -> Account:
        """Actualiza una cuenta existente"""
        pass

    @abstractmethod
    def delete(self, account_id: int) -> bool:
        """Elimina una cuenta por su ID"""
        pass

    @abstractmethod
    def exists_by_account_number(self, account_number: str) -> bool:
        """Verifica si existe una cuenta con el número de cuenta dado"""
        pass
