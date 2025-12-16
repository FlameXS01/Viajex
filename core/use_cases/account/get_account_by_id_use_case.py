from core.entities.account import Account
from core.repositories.account_repository import AccountRepository
from typing import Optional

class GetAccountByIdUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self, account_id: int) -> Optional[Account]:
        """Obtiene una cuenta por su ID"""
        if not account_id or account_id <= 0:
            raise ValueError("El ID de la cuenta debe ser un número positivo")
        
        return self.account_repository.get_by_id(account_id)