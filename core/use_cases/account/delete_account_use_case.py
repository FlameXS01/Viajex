from core.repositories.account_repository import AccountRepository

class DeleteAccountUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self, account_id: int) -> bool:
        """Elimina una cuenta por su ID"""
        # Validación básica
        if not account_id or account_id <= 0:
            raise ValueError("El ID de la cuenta debe ser un número positivo")
        
        # Verificar si la cuenta existe
        account = self.account_repository.get_by_id(account_id)
        if not account:
            return False
        
        # Eliminar la cuenta
        return self.account_repository.delete(account_id)