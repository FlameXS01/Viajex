from typing import Optional
from core.entities.account import Account
from core.repositories.account_repository import AccountRepository

class UpdateAccountUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self, account_id: int, account_number: str, description: str = None) -> Optional[Account]:
        """Actualiza una cuenta existente"""
        # Validaciones básicas
        if not account_id or account_id <= 0:
            raise ValueError("El ID de la cuenta debe ser un número positivo")
        
        if not account_number or account_number.strip() == "":
            raise ValueError("El número de cuenta no puede estar vacío")
        
        # Obtener la cuenta existente
        existing_account = self.account_repository.get_by_id(account_id)
        if not existing_account:
            raise ValueError(f"Cuenta con ID {account_id} no encontrada")
        
        # Verificar si el nuevo número de cuenta ya existe (excluyendo la cuenta actual)
        other_account = self.account_repository.get_by_account_number(account_number)
        if other_account and hasattr(other_account, 'id') and other_account.id != account_id:
            raise ValueError(f"Ya existe otra cuenta con el número {account_number}")
        
        # Actualizar los datos
        existing_account.account = account_number.strip()
        existing_account.description = description.strip() if description else None
        
        # Guardar los cambios
        return self.account_repository.update(existing_account)