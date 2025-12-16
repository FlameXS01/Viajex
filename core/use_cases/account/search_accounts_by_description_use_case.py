from typing import List
from core.entities.account import Account
from core.repositories.account_repository import AccountRepository

class SearchAccountsByDescriptionUseCase:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def execute(self, keyword: str) -> List[Account]:
        """Busca cuentas por palabra clave en la descripción"""
        if not keyword or keyword.strip() == "":
            raise ValueError("La palabra clave de búsqueda no puede estar vacía")
        
        # Asumiendo que el repositorio tiene un método search_by_description
        # Si no, podemos implementar la lógica aquí
        try:
            return self.account_repository.search_by_description(keyword)
        except AttributeError:
            # Si el repositorio no tiene el método, implementamos la búsqueda manual
            all_accounts = self.account_repository.get_all()
            keyword_lower = keyword.lower()
            
            return [
                account for account in all_accounts 
                if account.description and keyword_lower in account.description.lower()
            ]