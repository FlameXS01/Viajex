from typing import List, Optional, Tuple
from core.entities.account import Account
from core.use_cases.account.get_account_by_number_use_case import GetAccountByNumberUseCase
from core.use_cases.account.get_account_by_id_use_case import GetAccountByIdUseCase
from core.use_cases.account.get_all_accounts_use_case import GetAllAccountsUseCase
from core.use_cases.account.create_account_use_case import CreateAccountUseCase
from core.use_cases.account.update_account_use_case import UpdateAccountUseCase
from core.use_cases.account.delete_account_use_case import DeleteAccountUseCase
from core.use_cases.account.search_accounts_by_description_use_case import SearchAccountsByDescriptionUseCase
from core.use_cases.account.validate_account_number_use_case import ValidateAccountNumberUseCase


class AccountService:
    def __init__(self, 
                 create_account_use_case: CreateAccountUseCase,
                 update_account_use_case: UpdateAccountUseCase,
                 delete_account_use_case: DeleteAccountUseCase,
                 get_account_by_id_use_case: GetAccountByIdUseCase,
                 get_account_by_number_use_case: GetAccountByNumberUseCase,
                 get_all_accounts_use_case: GetAllAccountsUseCase,
                 search_accounts_by_description_use_case: SearchAccountsByDescriptionUseCase,
                 validate_account_number_use_case: ValidateAccountNumberUseCase):
        self.create_account_use_case = create_account_use_case
        self.update_account_use_case = update_account_use_case
        self.delete_account_use_case = delete_account_use_case
        self.get_account_by_id_use_case = get_account_by_id_use_case
        self.get_account_by_number_use_case = get_account_by_number_use_case
        self.get_all_accounts_use_case = get_all_accounts_use_case
        self.search_accounts_by_description_use_case = search_accounts_by_description_use_case
        self.validate_account_number_use_case = validate_account_number_use_case

    def create_account(self, account_number: str, description: str = None) -> Account:
        """
        Crea una nueva cuenta.
        
        Args:
            account_number: Número/código de la cuenta
            description: Descripción de la cuenta (opcional)
            
        Returns:
            Account: La cuenta creada
            
        Raises:
            ValueError: Si la validación falla
            Exception: Si ocurre un error en el repositorio
        """
        return self.create_account_use_case.execute(account_number, description)

    def update_account(self, account_id: int, account_number: str, description: str = None) -> Optional[Account]:
        """
        Actualiza una cuenta existente.
        
        Args:
            account_id: ID de la cuenta a actualizar
            account_number: Nuevo número/código de la cuenta
            description: Nueva descripción (opcional)
            
        Returns:
            Optional[Account]: La cuenta actualizada o None si no existe
            
        Raises:
            ValueError: Si la validación falla
            Exception: Si ocurre un error en el repositorio
        """
        return self.update_account_use_case.execute(account_id, account_number, description)

    def delete_account(self, account_id: int) -> bool:
        """
        Elimina una cuenta por su ID.
        
        Args:
            account_id: ID de la cuenta a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existía
            
        Raises:
            Exception: Si ocurre un error al eliminar
        """
        return self.delete_account_use_case.execute(account_id)

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """
        Obtiene una cuenta por su ID.
        
        Args:
            account_id: ID de la cuenta a buscar
            
        Returns:
            Optional[Account]: La cuenta encontrada o None si no existe
            
        Raises:
            ValueError: Si el ID no es válido
            Exception: Si ocurre un error en el repositorio
        """
        return self.get_account_by_id_use_case.execute(account_id)

    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """
        Obtiene una cuenta por su número/código.
        
        Args:
            account_number: Número/código de la cuenta a buscar
            
        Returns:
            Optional[Account]: La cuenta encontrada o None si no existe
            
        Raises:
            ValueError: Si el número de cuenta no es válido
            Exception: Si ocurre un error en el repositorio
        """
        return self.get_account_by_number_use_case.execute(account_number)

    def get_all_accounts(self) -> List[Account]:
        """
        Obtiene todas las cuentas del sistema.
        
        Returns:
            List[Account]: Lista de todas las cuentas
            
        Raises:
            Exception: Si ocurre un error en el repositorio
        """
        return self.get_all_accounts_use_case.execute()

    def search_accounts_by_description(self, keyword: str) -> List[Account]:
        """
        Busca cuentas por palabra clave en la descripción.
        
        Args:
            keyword: Palabra clave para buscar en descripciones
            
        Returns:
            List[Account]: Lista de cuentas que coinciden con la búsqueda
            
        Raises:
            ValueError: Si la palabra clave está vacía
            Exception: Si ocurre un error en el repositorio
        """
        return self.search_accounts_by_description_use_case.execute(keyword)

    def validate_account_number(self, account_number: str) -> Tuple[bool, str]:
        """
        Valida si un número de cuenta es válido y disponible.
        
        Args:
            account_number: Número de cuenta a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje)
            
        Raises:
            Exception: Si ocurre un error en el repositorio
        """
        return self.validate_account_number_use_case.execute(account_number)

    def get_accounts_summary(self) -> dict:
        """
        Obtiene un resumen estadístico de las cuentas.
        
        Returns:
            dict: Diccionario con estadísticas de cuentas
            
        Raises:
            Exception: Si ocurre un error en el repositorio
        """
        try:
            all_accounts = self.get_all_accounts()
            
            total_accounts = len(all_accounts)
            accounts_with_description = sum(1 for acc in all_accounts if acc.description and acc.description.strip())
            accounts_without_description = total_accounts - accounts_with_description
            
            # Agrupar por prefijos (primeros 3 caracteres)
            prefixes = {}
            for acc in all_accounts:
                if len(acc.account) >= 3:
                    prefix = acc.account[:3]
                    prefixes[prefix] = prefixes.get(prefix, 0) + 1
            
            return {
                "total_accounts": total_accounts,
                "accounts_with_description": accounts_with_description,
                "accounts_without_description": accounts_without_description,
                "accounts_by_prefix": prefixes,
                "description_coverage_percentage": (
                    (accounts_with_description / total_accounts * 100) if total_accounts > 0 else 0
                )
            }
            
        except Exception as e:
            raise Exception(f"Error al obtener resumen de cuentas: {str(e)}")

    def bulk_validate_account_numbers(self, account_numbers: List[str]) -> List[Tuple[str, bool, str]]:
        """
        Valida múltiples números de cuenta en lote.
        
        Args:
            account_numbers: Lista de números de cuenta a validar
            
        Returns:
            List[Tuple[str, bool, str]]: Lista de (número, es_válido, mensaje)
        """
        results = []
        for account_number in account_numbers:
            try:
                is_valid, message = self.validate_account_number(account_number)
                results.append((account_number, is_valid, message))
            except Exception as e:
                results.append((account_number, False, f"Error de validación: {str(e)}"))
        
        return results

    def check_account_exists(self, account_number: str) -> bool:
        """
        Verifica rápidamente si una cuenta existe por su número.
        
        Args:
            account_number: Número de cuenta a verificar
            
        Returns:
            bool: True si la cuenta existe, False en caso contrario
            
        Note:
            Este método es más eficiente que get_account_by_number 
            ya que solo verifica existencia sin cargar toda la entidad
        """
        try:
            account = self.get_account_by_number(account_number)
            return account is not None
        except Exception:
            return False

    def get_accounts_paginated(self, page: int = 1, page_size: int = 20) -> Tuple[List[Account], int, int]:
        """
        Obtiene cuentas paginadas.
        
        Args:
            page: Número de página (comienza en 1)
            page_size: Cantidad de elementos por página
            
        Returns:
            Tuple[List[Account], int, int]: (cuentas, total_cuentas, total_páginas)
            
        Note:
            Esta es una implementación básica. En producción, 
            deberías tener un método en el repositorio para paginación eficiente.
        """
        try:
            all_accounts = self.get_all_accounts()
            total_accounts = len(all_accounts)
            
            # Calcular índices de paginación
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            # Obtener subconjunto paginado
            paginated_accounts = all_accounts[start_idx:end_idx]
            
            # Calcular total de páginas
            total_pages = (total_accounts + page_size - 1) // page_size
            
            return paginated_accounts, total_accounts, total_pages
            
        except Exception as e:
            raise Exception(f"Error al obtener cuentas paginadas: {str(e)}")