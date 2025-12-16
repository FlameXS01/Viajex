from core.entities.account import Account
from core.repositories.account_repository import AccountRepository
from typing import Optional

class GetAccountByNumberUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self, account_number: str) -> Optional[Account]:
        """Obtiene una cuenta por su número/código"""
        if not account_number or account_number.strip() == "":
            raise ValueError("El número de cuenta no puede estar vacío")
        
        return self.account_repository.get_by_account_number(account_number)