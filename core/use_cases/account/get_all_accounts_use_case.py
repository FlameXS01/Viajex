from typing import List
from core.entities.account import Account
from core.repositories.account_repository import AccountRepository

class GetAllAccountsUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self) -> List[Account]:
        """Obtiene todas las cuentas del sistema"""
        return self.account_repository.get_all()