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
            
            if existing_by_number and existing_by_number.id != getattr(account, 'id', None):
                raise Exception(f"Ya existe una cuenta con el número {account.account}")
            
            existing_by_id = None
            if hasattr(account, 'id') and account.id:
                existing_by_id = self.db.query(AccountModel).filter(
                    AccountModel.account_id == account.id
                ).first()
            
            if existing_by_id:
                return self._update_existing_account(existing_by_id, account)
            else:
                return self._create_new_account(account)
                
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"IntegrityError al guardar cuenta: {str(e)}")
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e).lower():
                raise Exception(f"Ya existe una cuenta con el número {account.account_number}")
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
            account_number=account.account_number,
            account_type=getattr(account, 'account_type', 'checking'),
            balance=float(account.balance) if account.balance is not None else 0.0,
            currency=getattr(account, 'currency', 'USD'),
            is_active=getattr(account, 'is_active', True),
            customer_id=getattr(account, 'customer_id', None),
            created_at=getattr(account, 'created_at', None),
            updated_at=getattr(account, 'updated_at', None)
        )
        
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        
        logger.info(f"Nueva cuenta creada: {db_account.account_number} (ID: {db_account.account_id})")
        return self._to_entity(db_account)
    
    def _update_existing_account(self, db_account: AccountModel, account: Account) -> Account:
        """Actualiza una cuenta existente en la base de datos"""
        # Actualizar solo los campos que están presentes en la entidad
        if hasattr(account, 'account_number'):
            db_account.account_number = account.account_number
        if hasattr(account, 'account_type'):
            db_account.account_type = account.account_type
        if hasattr(account, 'balance'):
            db_account.balance = float(account.balance) if account.balance is not None else db_account.balance
        if hasattr(account, 'currency'):
            db_account.currency = account.currency
        if hasattr(account, 'is_active'):
            db_account.is_active = account.is_active
        if hasattr(account, 'customer_id'):
            db_account.customer_id = account.customer_id
        
        # Siempre actualizar la marca de tiempo
        from datetime import datetime
        db_account.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_account)
        
        logger.info(f"Cuenta actualizada: {db_account.account_number} (ID: {db_account.account_id})")
        return self._to_entity(db_account)
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Obtiene una cuenta por ID desde la base de datos"""
        try:
            db_account = self.db.query(AccountModel).filter(
                AccountModel.account_id == account_id
            ).first()
            
            return self._to_entity(db_account) if db_account else None
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener cuenta por ID {account_id}: {str(e)}")
            raise Exception(f"Error de base de datos al obtener cuenta: {str(e)}")
    
    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Obtiene una cuenta por número de cuenta desde la base de datos"""
        try:
            db_account = self.db.query(AccountModel).filter(
                AccountModel.account_number == account_number
            ).first()
            
            return self._to_entity(db_account) if db_account else None
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener cuenta por número {account_number}: {str(e)}")
            raise Exception(f"Error de base de datos al obtener cuenta: {str(e)}")
    
    def get_all(self) -> List[Account]:
        """Obtiene todas las cuentas del sistema"""
        try:
            db_accounts = self.db.query(AccountModel).order_by(
                AccountModel.created_at.desc()
            ).all()
            
            return [self._to_entity(account) for account in db_accounts]
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener todas las cuentas: {str(e)}")
            raise Exception(f"Error de base de datos al obtener cuentas: {str(e)}")
    
    def update(self, account: Account) -> Account:
        """Actualiza una cuenta existente en la base de datos"""
        # Este método es básicamente un alias de save, pero lo implementamos
        # para mantener la interfaz consistente
        return self.save(account)
    
    def delete(self, account_id: int) -> bool:
        """Elimina una cuenta por su ID con validaciones"""
        try:
            db_account = self.db.query(AccountModel).filter(
                AccountModel.account_id == account_id
            ).first()
            
            if not db_account:
                logger.warning(f"Intento de eliminar cuenta inexistente: ID {account_id}")
                return False
            
            # Validaciones de negocio antes de eliminar
            if db_account.balance > 0:
                raise Exception(
                    f"No se puede eliminar la cuenta '{db_account.account_number}'. "
                    f"Tiene un saldo de ${db_account.balance:.2f}. "
                    f"Transfiera o retire el saldo primero."
                )
            
            # Verificar si la cuenta está activa
            if db_account.is_active:
                raise Exception(
                    f"No se puede eliminar la cuenta '{db_account.account_number}' porque está activa. "
                    f"Desactive la cuenta primero."
                )
            
            # Aquí podrías agregar más validaciones, como verificar si hay
            # transacciones asociadas, etc.
            
            self.db.delete(db_account)
            self.db.commit()
            
            logger.info(f"Cuenta eliminada: {db_account.account_number} (ID: {db_account.account_id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            if "No se puede eliminar" in str(e):
                raise e  # Re-lanzar excepciones de negocio
            logger.error(f"Error al eliminar cuenta ID {account_id}: {str(e)}")
            raise Exception(f"Error al eliminar cuenta: {str(e)}")
    
    def exists_by_account_number(self, account_number: str) -> bool:
        """Verifica si existe una cuenta con el número de cuenta dado"""
        try:
            count = self.db.query(AccountModel).filter(
                AccountModel.account_number == account_number
            ).count()
            
            return count > 0
            
        except SQLAlchemyError as e:
            logger.error(f"Error al verificar existencia de cuenta {account_number}: {str(e)}")
            raise Exception(f"Error de base de datos al verificar cuenta: {str(e)}")
    
    # Métodos adicionales útiles (no en la interfaz abstracta pero comunes)
    
    def get_by_customer_id(self, customer_id: int) -> List[Account]:
        """Obtiene todas las cuentas de un cliente específico"""
        try:
            db_accounts = self.db.query(AccountModel).filter(
                AccountModel.customer_id == customer_id
            ).order_by(AccountModel.account_type).all()
            
            return [self._to_entity(account) for account in db_accounts]
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener cuentas del cliente {customer_id}: {str(e)}")
            raise Exception(f"Error de base de datos al obtener cuentas del cliente: {str(e)}")
    
    def get_active_accounts(self, is_active: bool = True) -> List[Account]:
        """Obtiene cuentas por estado de actividad"""
        try:
            db_accounts = self.db.query(AccountModel).filter(
                AccountModel.is_active == is_active
            ).order_by(AccountModel.account_number).all()
            
            return [self._to_entity(account) for account in db_accounts]
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener cuentas activas={is_active}: {str(e)}")
            raise Exception(f"Error de base de datos al obtener cuentas: {str(e)}")
    
    def transfer_funds(self, from_account_id: int, to_account_id: int, amount: float) -> bool:
        """Transfiere fondos entre cuentas"""
        if amount <= 0:
            raise Exception("El monto de transferencia debe ser mayor a cero")
        
        try:
            # Obtener ambas cuentas
            from_account = self.db.query(AccountModel).filter(
                AccountModel.account_id == from_account_id
            ).with_for_update().first()
            
            to_account = self.db.query(AccountModel).filter(
                AccountModel.account_id == to_account_id
            ).with_for_update().first()
            
            if not from_account or not to_account:
                raise Exception("Una o ambas cuentas no existen")
            
            if not from_account.is_active:
                raise Exception(f"La cuenta origen '{from_account.account_number}' no está activa")
            
            if not to_account.is_active:
                raise Exception(f"La cuenta destino '{to_account.account_number}' no está activa")
            
            if from_account.balance < amount:
                raise Exception(
                    f"Saldo insuficiente en la cuenta '{from_account.account_number}'. "
                    f"Saldo disponible: ${from_account.balance:.2f}"
                )
            
            # Realizar la transferencia
            from_account.balance -= amount
            to_account.balance += amount
            
            # Actualizar timestamps
            from datetime import datetime
            from_account.updated_at = datetime.utcnow()
            to_account.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(
                f"Transferencia realizada: ${amount:.2f} desde cuenta {from_account.account_number} "
                f"a {to_account.account_number}"
            )
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error en transferencia: {str(e)}")
            if "Saldo insuficiente" in str(e) or "no está activa" in str(e):
                raise e  # Re-lanzar excepciones de negocio
            raise Exception(f"Error en transferencia: {str(e)}")
    
    def _to_entity(self, db_account: AccountModel) -> Optional[Account]:
        """Convierte un modelo de SQLAlchemy a una entidad de dominio"""
        if not db_account:
            return None
        
        return Account(
            id=db_account.id,
            account_number=db_account.account_number,
            account_type=db_account.account_type,
            balance=float(db_account.balance) if db_account.balance is not None else 0.0,
            currency=db_account.currency,
            is_active=db_account.is_active,
            customer_id=db_account.customer_id,
            created_at=db_account.created_at,
            updated_at=db_account.updated_at
        )