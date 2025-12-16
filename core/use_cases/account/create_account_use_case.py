from core.entities.account import Account
from core.repositories.account_repository import AccountRepository

class CreateAccountUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self, account_number: str, description: str = None) -> Account:
        """Crea una nueva cuenta"""
        # Validaciones
        if not account_number or account_number.strip() == "":
            raise ValueError("El número de cuenta no puede estar vacío")
        
        # Validar formato del número de cuenta (puedes ajustar según tus reglas)
        if len(account_number) > 50:
            raise ValueError("El número de cuenta no puede exceder 50 caracteres")
        
        # Verificar si ya existe una cuenta con ese número
        if self.account_repository.exists_by_account_number(account_number):
            raise ValueError(f"Ya existe una cuenta con el número {account_number}")
        
        # Crear la entidad
        new_account = Account(
            account=account_number.strip(),
            description=description.strip() if description else None
        )
        
        # Guardar en el repositorio
        return self.account_repository.save(new_account)