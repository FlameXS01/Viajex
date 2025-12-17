from abc import ABC, abstractmethod
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from core.entities.card_transaction import CardTransaction
from core.entities.card_balance_snapshot import CardBalanceSnapshot


class CardTransactionRepository(ABC):
    """
    Interfaz abstracta para el repositorio de transacciones de tarjetas.
    
    Define las operaciones CRUD y consultas específicas para
    la trazabilidad de transacciones.
    """
    
    @abstractmethod
    def save(self, transaction: CardTransaction) -> CardTransaction:
        """
        Guarda una nueva transacción de tarjeta.
        
        Args:
            transaction: Entidad CardTransaction a guardar
            
        Returns:
            CardTransaction: La transacción guardada con ID asignado
        """
        pass
    
    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Optional[CardTransaction]:
        """
        Obtiene una transacción por su ID.
        
        Args:
            transaction_id: ID de la transacción
            
        Returns:
            Optional[CardTransaction]: La transacción encontrada o None
        """
        pass
    
    @abstractmethod
    def get_by_card_id(
        self, 
        card_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[CardTransaction]:
        """
        Obtiene transacciones de una tarjeta con filtros opcionales.
        
        Args:
            card_id: ID de la tarjeta
            start_date: Fecha inicial del rango (inclusive)
            end_date: Fecha final del rango (inclusive)
            transaction_type: Tipo de transacción a filtrar
            limit: Límite de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            List[CardTransaction]: Lista de transacciones que coinciden
        """
        pass
    
    @abstractmethod
    def count_by_card_id(
        self,
        card_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None
    ) -> int:
        """
        Cuenta transacciones de una tarjeta con filtros.
        
        Args:
            card_id: ID de la tarjeta
            start_date: Fecha inicial del rango
            end_date: Fecha final del rango
            transaction_type: Tipo de transacción
            
        Returns:
            int: Número total de transacciones que coinciden
        """
        pass
    
    @abstractmethod
    def get_balance_at_date(self, card_id: int, target_date: datetime) -> Decimal:
        """
        Obtiene el balance de una tarjeta en una fecha y hora específica.
        
        Args:
            card_id: ID de la tarjeta
            target_date: Fecha y hora para consultar el balance
            
        Returns:
            Decimal: Balance de la tarjeta en la fecha especificada
        """
        pass
    
    @abstractmethod
    def get_transactions_by_reference(
        self, 
        reference_type: str, 
        reference_id: int
    ) -> List[CardTransaction]:
        """
        Obtiene transacciones por referencia (ej: todas las de una dieta).
        
        Args:
            reference_type: Tipo de referencia (diet, liquidation, etc.)
            reference_id: ID de la entidad referenciada
            
        Returns:
            List[CardTransaction]: Transacciones relacionadas
        """
        pass
    
    @abstractmethod
    def get_summary_by_card_and_period(
        self,
        card_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen estadístico de transacciones en un período.
        
        Args:
            card_id: ID de la tarjeta
            start_date: Fecha inicial
            end_date: Fecha final
            
        Returns:
            Dict con estadísticas del período
        """
        pass


class CardBalanceSnapshotRepository(ABC):
    """
    Interfaz abstracta para el repositorio de snapshots de balances.
    
    Optimiza consultas históricas mediante datos precalculados.
    """
    
    @abstractmethod
    def save(self, snapshot: CardBalanceSnapshot) -> CardBalanceSnapshot:
        """
        Guarda un snapshot diario de balance.
        
        Args:
            snapshot: Entidad CardBalanceSnapshot a guardar
            
        Returns:
            CardBalanceSnapshot: El snapshot guardado
        """
        pass
    
    @abstractmethod
    def get_by_card_and_date(
        self, 
        card_id: int, 
        snapshot_date: date
    ) -> Optional[CardBalanceSnapshot]:
        """
        Obtiene un snapshot para una tarjeta en una fecha específica.
        
        Args:
            card_id: ID de la tarjeta
            snapshot_date: Fecha del snapshot
            
        Returns:
            Optional[CardBalanceSnapshot]: El snapshot encontrado o None
        """
        pass
    
    @abstractmethod
    def get_by_card_and_month(
        self, 
        card_id: int, 
        year: int, 
        month: int
    ) -> List[CardBalanceSnapshot]:
        """
        Obtiene todos los snapshots de una tarjeta en un mes específico.
        
        Args:
            card_id: ID de la tarjeta
            year: Año
            month: Mes (1-12)
            
        Returns:
            List[CardBalanceSnapshot]: Snapshots del mes
        """
        pass
    
    @abstractmethod
    def get_monthly_summary(
        self, 
        card_id: int, 
        year: int, 
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene resumen mensual o anual de una tarjeta.
        
        Args:
            card_id: ID de la tarjeta
            year: Año
            month: Mes (1-12) o None para resumen anual
            
        Returns:
            Dict con resumen del período
        """
        pass
    
    @abstractmethod
    def delete_snapshots_before_date(self, cutoff_date: date) -> int:
        """
        Elimina snapshots antiguos para mantenimiento.
        
        Args:
            cutoff_date: Fecha límite (snapshots anteriores se eliminan)
            
        Returns:
            int: Número de snapshots eliminados
        """
        pass