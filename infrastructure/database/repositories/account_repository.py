from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional
from core.entities.account import Account
from core.repositories.account_repository import AccountRepository
from infrastructure.database.models import AccountModel
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class AccountRepositoryImpl(AccountRepository):
    """Implementación concreta del repositorio de cuentas usando SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, account: Account) -> Account:
        """Guarda o actualiza una cuenta en la base de datos"""
        try:
            existing_by_number = self.db.query(AccountModel).filter(
                AccountModel.account == account.account
            ).first()
            
            if hasattr(account, 'id') and account.id:
                existing_by_id = self.db.query(AccountModel).filter(
                    AccountModel.id == account.id
                ).first()
                
                if existing_by_number and existing_by_number.id != account.id:
                    raise Exception(f"Ya existe una cuenta con el código {account.account}")
                
                if existing_by_id:
                    return self._update_existing_account(existing_by_id, account)
                else:
                    return self._create_new_account_with_id(account)
            else:
                if existing_by_number:
                    raise Exception(f"Ya existe una cuenta con el código {account.account}")
                
                return self._create_new_account(account)
                
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError al guardar cuenta: {str(e)}")
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e).lower():
                raise Exception(f"Ya existe una cuenta con el código {account.account}")
            raise Exception(f"Error de integridad al guardar cuenta: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"SQLAlchemyError al guardar cuenta: {str(e)}")
            raise Exception(f"Error de base de datos al guardar cuenta: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error inesperado al guardar cuenta: {str(e)}")
            raise
    
    def _create_new_account(self, account: Account) -> Account:
        """Crea una nueva cuenta en la base de datos"""
        db_account = AccountModel(
            account=account.account,
            description=account.description if hasattr(account, 'description') else None
        )
        
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        
        return self._to_entity(db_account)
    
    def _create_new_account_with_id(self, account: Account) -> Account:
        """Crea una nueva cuenta con ID específico (para casos especiales)"""
        db_account = AccountModel(
            id=account.id if hasattr(account, 'id') else None,
            account=account.account,
            description=account.description if hasattr(account, 'description') else None
        )
        
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        
        return self._to_entity(db_account)
    
    def _update_existing_account(self, db_account: AccountModel, account: Account) -> Account:
        """Actualiza una cuenta existente en la base de datos"""
        db_account.account = account.account
        if hasattr(account, 'description'):
            db_account.description = account.description
        
        self.db.commit()
        self.db.refresh(db_account)
        
        return self._to_entity(db_account)
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Obtiene una cuenta por ID desde la base de datos"""
        try:
            db_account = self.db.query(AccountModel).filter(
                AccountModel.id == account_id
            ).first()
            
            return self._to_entity(db_account) if db_account else None
            
        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos al obtener cuenta: {str(e)}")
    
    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Obtiene una cuenta por su número/código de cuenta"""
        try:
            db_account = self.db.query(AccountModel).filter(
                AccountModel.account == account_number
            ).first()
            
            return self._to_entity(db_account) if db_account else None
            
        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos al obtener cuenta: {str(e)}")
    
    def get_all(self) -> List[Account]:
        """Obtiene todas las cuentas del sistema"""
        try:
            db_accounts = self.db.query(AccountModel).order_by(
                AccountModel.account.asc()
            ).all()
            
            return [self._to_entity(account) for account in db_accounts]
            
        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos al obtener cuentas: {str(e)}")
    
    def update(self, account: Account) -> Account:
        """Actualiza una cuenta existente"""
        if not hasattr(account, 'id') or not account.id:
            raise Exception("No se puede actualizar una cuenta sin ID")
        
        return self.save(account)
    
    def delete(self, account_id: int) -> bool:
        """Elimina una cuenta por su ID"""
        try:
            db_account = self.db.query(AccountModel).filter(
                AccountModel.id == account_id
            ).first()   
            
            self.db.delete(db_account)
            self.db.commit()
            
            logger.info(f"Cuenta eliminada: {db_account.account} (ID: {db_account.id})")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            
            if "foreign key constraint" in str(e).lower() or "integrity constraint" in str(e).lower():
                raise Exception(f"No se puede eliminar la cuenta porque está siendo utilizada en otras tablas")
            
            raise Exception(f"Error de base de datos al eliminar cuenta: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar cuenta: {str(e)}")
    
    def exists_by_account_number(self, account_number: str) -> bool:
        """Verifica si existe una cuenta con el número/código de cuenta dado"""
        try:
            count = self.db.query(AccountModel).filter(
                AccountModel.account == account_number
            ).count()
            
            return count > 0
            
        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos al verificar cuenta: {str(e)}")
    
    def search_by_description(self, keyword: str) -> List[Account]:
        """Busca cuentas por palabra clave en la descripción"""
        try:
            db_accounts = self.db.query(AccountModel).filter(
                AccountModel.description.ilike(f"%{keyword}%")
            ).order_by(AccountModel.account.asc()).all()
            
            return [self._to_entity(account) for account in db_accounts]
            
        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos al buscar cuentas: {str(e)}")
    
    def get_by_account_pattern(self, pattern: str) -> List[Account]:
        """Obtiene cuentas cuyo código coincide con un patrón"""
        try:
            db_accounts = self.db.query(AccountModel).filter(
                AccountModel.account.ilike(f"%{pattern}%")
            ).order_by(AccountModel.account.asc()).all()
            
            return [self._to_entity(account) for account in db_accounts]
            
        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos al buscar cuentas: {str(e)}")
    
    def get_accounts_without_description(self) -> List[Account]:
        """Obtiene cuentas que no tienen descripción"""
        try:
            db_accounts = self.db.query(AccountModel).filter(
                AccountModel.description.is_(None) | 
                (AccountModel.description == "")
            ).order_by(AccountModel.account.asc()).all()
            
            return [self._to_entity(account) for account in db_accounts]
            
        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos al obtener cuentas: {str(e)}")
    
    def bulk_create(self, accounts: List[Account]) -> List[Account]:
        """Crea múltiples cuentas en lote"""
        if not accounts:
            return []
        
        created_accounts = []
        try:
            for account in accounts:
                if not self.exists_by_account_number(account.account):
                    db_account = AccountModel(
                        account=account.account,
                        description=account.description if hasattr(account, 'description') else None
                    )
                    self.db.add(db_account)
                    created_accounts.append(account)
            
            self.db.commit()
            
            result = []
            for acc in created_accounts:
                db_acc = self.db.query(AccountModel).filter(
                    AccountModel.account == acc.account
                ).first()
                if db_acc:
                    result.append(self._to_entity(db_acc))
            
            return result
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos en creación en lote: {str(e)}")
    
    def _to_entity(self, db_account: AccountModel) -> Optional[Account]:
        """Convierte un modelo de SQLAlchemy a una entidad de dominio"""
        if not db_account:
            return None
        
        account_entity = Account(
            account=db_account.account,
            description=db_account.description
        )
        
        if hasattr(account_entity, 'id'):
            account_entity.id = db_account.id
        else:
            account_entity.id = db_account.id
        
        return account_entity