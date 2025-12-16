from core.repositories.account_repository import AccountRepository

class ValidateAccountNumberUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self, account_number: str) -> tuple[bool, str]:
        """Valida si un número de cuenta es válido y disponible"""
        if not account_number or account_number.strip() == "":
            return False, "El número de cuenta no puede estar vacío"
        
        # Validar longitud máxima
        if len(account_number) > 50:
            return False, "El número de cuenta no puede exceder 50 caracteres"
        
        # Validar caracteres permitidos (ajustar según necesidades)
        # Por ejemplo, solo alfanumérico y algunos símbolos
        import re
        if not re.match(r'^[A-Za-z0-9\-_]+$', account_number):
            return False, "El número de cuenta solo puede contener letras, números, guiones y guiones bajos"
        
        # Verificar si ya existe
        if self.account_repository.exists_by_account_number(account_number):
            return False, f"El número de cuenta '{account_number}' ya está en uso"
        
        return True, "Número de cuenta válido"