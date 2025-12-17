from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from sqlalchemy.exc import SQLAlchemyError

from core.entities.card_transaction import CardTransaction
from core.entities.card_balance_snapshot import CardBalanceSnapshot
from core.repositories.card_transaction_repository import (
    CardTransactionRepository, 
    CardBalanceSnapshotRepository
)
from infrastructure.database.models import (
    CardTransactionModel, 
    CardBalanceSnapshotModel,
    CardModel
)
import logging

logger = logging.getLogger(__name__)


class CardTransactionRepositoryImpl(CardTransactionRepository):
    """
    Implementación concreta del repositorio de transacciones usando SQLAlchemy.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, transaction: CardTransaction) -> CardTransaction:
        """Guarda una transacción con manejo de errores y auditoría."""
        try:
            db_transaction = CardTransactionModel(
                card_id=transaction.card_id,
                transaction_type=transaction.transaction_type,
                amount=transaction.amount,
                previous_balance=transaction.previous_balance,
                new_balance=transaction.new_balance,
                operation_date=transaction.operation_date,
                diet_id=transaction.diet_id,
                liquidation_id=transaction.liquidation_id,
                notes=transaction.notes
            )
            
            self.db.add(db_transaction)
            self.db.flush()  # Para obtener el ID sin commit
            
            # Actualizar entidad con ID generado
            transaction.id = db_transaction.id
            transaction.recorded_at = db_transaction.recorded_at
            
            logger.info(
                f"Transacción guardada: ID={db_transaction.id}, "
                f"Tarjeta={db_transaction.card_id}, "
                f"Monto={db_transaction.amount}"
            )
            
            return transaction
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al guardar transacción: {str(e)}")
            raise Exception(f"Error de base de datos al guardar transacción: {str(e)}")
    
    def get_by_id(self, transaction_id: int) -> Optional[CardTransaction]:
        """Obtiene una transacción por ID."""
        try:
            db_transaction = self.db.query(CardTransactionModel).filter(
                CardTransactionModel.id == transaction_id
            ).first()
            
            return self._to_entity(db_transaction) if db_transaction else None
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener transacción {transaction_id}: {str(e)}")
            raise Exception(f"Error de base de datos al obtener transacción: {str(e)}")
    
    def get_by_card_id(
        self, 
        card_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[CardTransaction]:
        """Obtiene transacciones de una tarjeta con filtros."""
        try:
            query = self.db.query(CardTransactionModel).filter(
                CardTransactionModel.card_id == card_id
            )
            
            # Aplicar filtros
            if start_date:
                query = query.filter(CardTransactionModel.operation_date >= start_date)
            if end_date:
                query = query.filter(CardTransactionModel.operation_date <= end_date)
            if transaction_type:
                query = query.filter(CardTransactionModel.transaction_type == transaction_type)
            
            # Ordenar por fecha de operación (más recientes primero)
            query = query.order_by(CardTransactionModel.operation_date.desc())
            
            # Aplicar paginación
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            return [self._to_entity(t) for t in results]
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener transacciones de tarjeta {card_id}: {str(e)}")
            raise Exception(f"Error de base de datos al obtener transacciones: {str(e)}")
    
    def count_by_card_id(
        self,
        card_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None
    ) -> int:
        """Cuenta transacciones de una tarjeta con filtros."""
        try:
            query = self.db.query(func.count(CardTransactionModel.id)).filter(
                CardTransactionModel.card_id == card_id
            )
            
            if start_date:
                query = query.filter(CardTransactionModel.operation_date >= start_date)
            if end_date:
                query = query.filter(CardTransactionModel.operation_date <= end_date)
            if transaction_type:
                query = query.filter(CardTransactionModel.transaction_type == transaction_type)
            
            return query.scalar() or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Error al contar transacciones de tarjeta {card_id}: {str(e)}")
            raise Exception(f"Error de base de datos al contar transacciones: {str(e)}")
    
    def get_balance_at_date(self, card_id: int, target_date: datetime) -> float:
        """
        Obtiene el balance de una tarjeta en una fecha/hora específica.
        
        Utiliza la última transacción antes de la fecha objetivo.
        """
        try:
            # Buscar la última transacción antes de target_date
            last_transaction = self.db.query(CardTransactionModel).filter(
                CardTransactionModel.card_id == card_id,
                CardTransactionModel.operation_date <= target_date
            ).order_by(CardTransactionModel.operation_date.desc()).first()
            
            if last_transaction:
                # Balance después de la última transacción
                return float(str(last_transaction.new_balance))
            else:
                # Si no hay transacciones previas, verificar si la tarjeta existe
                card = self.db.query(CardModel).filter(CardModel.card_id == card_id).first()
                if card and card.balance is not None:
                    # Si la tarjeta existe pero no tiene transacciones, usar balance actual
                    # Esto solo debería pasar durante la migración
                    return float(str(card.balance))
                else:
                    # Tarjeta no encontrada o sin balance
                    return float('0')
                    
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener balance histórico: {str(e)}")
            raise Exception(f"Error de base de datos al obtener balance histórico: {str(e)}")
    
    def get_transactions_by_reference(
        self, 
        reference_type: str, 
        reference_id: int
    ) -> List[CardTransaction]:
        """Obtiene transacciones por referencia."""
        try:
            # Determinar qué campo usar según el tipo de referencia
            if reference_type == 'diet':
                filter_condition = CardTransactionModel.diet_id == reference_id
            elif reference_type == 'liquidation':
                filter_condition = CardTransactionModel.liquidation_id == reference_id
            else:
                # Para otros tipos, usar notes o transaction_type
                filter_condition = CardTransactionModel.transaction_type == reference_type
            
            results = self.db.query(CardTransactionModel).filter(
                filter_condition
            ).order_by(CardTransactionModel.operation_date).all()
            
            return [self._to_entity(t) for t in results]
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener transacciones por referencia: {str(e)}")
            raise Exception(f"Error de base de datos al obtener transacciones: {str(e)}")
    
    def get_summary_by_card_and_period(
        self,
        card_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Obtiene resumen estadístico de un período."""
        try:
            # Consulta para obtener totales por tipo
            summary_query = self.db.query(
                CardTransactionModel.transaction_type,
                func.count(CardTransactionModel.id).label('count'),
                func.sum(CardTransactionModel.amount).label('total_amount')
            ).filter(
                CardTransactionModel.card_id == card_id,
                CardTransactionModel.operation_date >= start_date,
                CardTransactionModel.operation_date <= end_date
            ).group_by(CardTransactionModel.transaction_type)
            
            results = summary_query.all()
            
            # Calcular totales generales
            total_credits = float('0')
            total_debits = float('0')
            by_type = {}
            
            for transaction_type, count, total_amount in results:
                amount_float = float(str(total_amount)) if total_amount else float('0')
                by_type[transaction_type] = {
                    'count': count,
                    'total_amount': amount_float
                }
                
                if amount_float > 0:
                    total_credits += amount_float
                else:
                    total_debits += abs(amount_float)
            
            # Obtener balance inicial y final del período
            opening_balance = self.get_balance_at_date(card_id, start_date)
            closing_balance = self.get_balance_at_date(card_id, end_date)
            
            return {
                'period': {'start': start_date, 'end': end_date},
                'opening_balance': opening_balance,
                'closing_balance': closing_balance,
                'total_credits': total_credits,
                'total_debits': total_debits,
                'net_movement': total_credits - total_debits,
                'transaction_count': sum(item['count'] for item in by_type.values()),
                'by_type': by_type
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener resumen del período: {str(e)}")
            raise Exception(f"Error de base de datos al obtener resumen: {str(e)}")
    
    def _to_entity(self, model: CardTransactionModel) -> Optional[CardTransaction]:
        """Convierte un modelo de SQLAlchemy a entidad de dominio."""
        if not model:
            return None
        
        return CardTransaction(
            id=model.id,
            card_id=model.card_id,
            transaction_type=model.transaction_type,
            amount=float(str(model.amount)) if model.amount else float('0'),
            previous_balance=float(str(model.previous_balance)) if model.previous_balance else float('0'),
            new_balance=float(str(model.new_balance)) if model.new_balance else float('0'),
            operation_date=model.operation_date,
            recorded_at=model.recorded_at,
            diet_id=model.diet_id,
            liquidation_id=model.liquidation_id,
            notes=model.notes
        )


class CardBalanceSnapshotRepositoryImpl(CardBalanceSnapshotRepository):
    """
    Implementación concreta del repositorio de snapshots usando SQLAlchemy.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, snapshot: CardBalanceSnapshot) -> CardBalanceSnapshot:
        """Guarda un snapshot con manejo de conflictos de unicidad."""
        try:
            # Verificar si ya existe un snapshot para esta tarjeta y fecha
            existing = self.get_by_card_and_date(snapshot.card_id, snapshot.snapshot_date)
            
            if existing:
                # Actualizar existente
                db_snapshot = self.db.query(CardBalanceSnapshotModel).filter(
                    CardBalanceSnapshotModel.id == existing.id
                ).first()
                
                if db_snapshot:
                    db_snapshot.opening_balance = snapshot.opening_balance
                    db_snapshot.closing_balance = snapshot.closing_balance
                    db_snapshot.total_credits = snapshot.total_credits
                    db_snapshot.total_debits = snapshot.total_debits
                    db_snapshot.transaction_count = snapshot.transaction_count
                    
                    snapshot.id = db_snapshot.id
                else:
                    raise Exception(f"Snapshot no encontrado para actualización")
            else:
                # Crear nuevo
                db_snapshot = CardBalanceSnapshotModel(
                    card_id=snapshot.card_id,
                    snapshot_date=snapshot.snapshot_date,
                    opening_balance=snapshot.opening_balance,
                    closing_balance=snapshot.closing_balance,
                    total_credits=snapshot.total_credits,
                    total_debits=snapshot.total_debits,
                    transaction_count=snapshot.transaction_count
                )
                self.db.add(db_snapshot)
                self.db.flush()
                snapshot.id = db_snapshot.id
            
            logger.info(
                f"Snapshot guardado: Tarjeta={snapshot.card_id}, "
                f"Fecha={snapshot.snapshot_date}, "
                f"Balance={snapshot.closing_balance}"
            )
            
            return snapshot
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al guardar snapshot: {str(e)}")
            raise Exception(f"Error de base de datos al guardar snapshot: {str(e)}")
    
    def get_by_card_and_date(
        self, 
        card_id: int, 
        snapshot_date: date
    ) -> Optional[CardBalanceSnapshot]:
        """Obtiene snapshot por tarjeta y fecha."""
        try:
            db_snapshot = self.db.query(CardBalanceSnapshotModel).filter(
                CardBalanceSnapshotModel.card_id == card_id,
                CardBalanceSnapshotModel.snapshot_date == snapshot_date
            ).first()
            
            return self._to_entity(db_snapshot) if db_snapshot else None
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener snapshot: {str(e)}")
            raise Exception(f"Error de base de datos al obtener snapshot: {str(e)}")
    
    def get_by_card_and_month(
        self, 
        card_id: int, 
        year: int, 
        month: int
    ) -> List[CardBalanceSnapshot]:
        """Obtiene snapshots de un mes específico."""
        try:
            db_snapshots = self.db.query(CardBalanceSnapshotModel).filter(
                CardBalanceSnapshotModel.card_id == card_id,
                extract('year', CardBalanceSnapshotModel.snapshot_date) == year,
                extract('month', CardBalanceSnapshotModel.snapshot_date) == month
            ).order_by(CardBalanceSnapshotModel.snapshot_date).all()
            
            return [self._to_entity(s) for s in db_snapshots]
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener snapshots del mes: {str(e)}")
            raise Exception(f"Error de base de datos al obtener snapshots: {str(e)}")
    
    def get_monthly_summary(
        self, 
        card_id: int, 
        year: int, 
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene resumen mensual o anual."""
        try:
            query = self.db.query(
                extract('month', CardBalanceSnapshotModel.snapshot_date).label('month'),
                func.sum(CardBalanceSnapshotModel.total_credits).label('total_credits'),
                func.sum(CardBalanceSnapshotModel.total_debits).label('total_debits'),
                func.sum(CardBalanceSnapshotModel.transaction_count).label('transaction_count')
            ).filter(
                CardBalanceSnapshotModel.card_id == card_id,
                extract('year', CardBalanceSnapshotModel.snapshot_date) == year
            )
            
            if month:
                query = query.filter(
                    extract('month', CardBalanceSnapshotModel.snapshot_date) == month
                )
            
            query = query.group_by(
                extract('month', CardBalanceSnapshotModel.snapshot_date)
            ).order_by('month')
            
            results = query.all()
            
            if month and results:
                # Resumen de un mes específico
                result = results[0]
                return {
                    'month': month,
                    'total_credits': float(str(result.total_credits)) if result.total_credits else float('0'),
                    'total_debits': float(str(result.total_debits)) if result.total_debits else float('0'),
                    'transaction_count': result.transaction_count or 0,
                    'net_movement': (float(str(result.total_credits)) if result.total_credits else float('0')) - 
                                   (float(str(result.total_debits)) if result.total_debits else float('0'))
                }
            elif not month:
                # Resumen anual (todos los meses)
                monthly_summaries = []
                annual_totals = {
                    'total_credits': float('0'),
                    'total_debits': float('0'),
                    'transaction_count': 0
                }
                
                for result in results:
                    month_credits = float(str(result.total_credits)) if result.total_credits else float('0')
                    month_debits = float(str(result.total_debits)) if result.total_debits else float('0')
                    
                    monthly_summaries.append({
                        'month': int(result.month),
                        'total_credits': month_credits,
                        'total_debits': month_debits,
                        'transaction_count': result.transaction_count or 0,
                        'net_movement': month_credits - month_debits
                    })
                    
                    annual_totals['total_credits'] += month_credits
                    annual_totals['total_debits'] += month_debits
                    annual_totals['transaction_count'] += result.transaction_count or 0
                
                annual_totals['net_movement'] = (
                    annual_totals['total_credits'] - annual_totals['total_debits']
                )
                
                return {
                    'year': year,
                    'monthly_summaries': monthly_summaries,
                    'annual_totals': annual_totals
                }
            
            return {}  # No hay datos
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener resumen mensual: {str(e)}")
            raise Exception(f"Error de base de datos al obtener resumen: {str(e)}")
    
    def delete_snapshots_before_date(self, cutoff_date: date) -> int:
        """Elimina snapshots antiguos."""
        try:
            result = self.db.query(CardBalanceSnapshotModel).filter(
                CardBalanceSnapshotModel.snapshot_date < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Eliminados {result} snapshots anteriores a {cutoff_date}")
            
            return result
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al eliminar snapshots: {str(e)}")
            raise Exception(f"Error de base de datos al eliminar snapshots: {str(e)}")
    
    def _to_entity(self, model: CardBalanceSnapshotModel) -> Optional[CardBalanceSnapshot]:
        """Convierte modelo a entidad."""
        if not model:
            return None
        
        return CardBalanceSnapshot(
            id=model.id,
            card_id=model.card_id,
            snapshot_date=model.snapshot_date,
            opening_balance=float(str(model.opening_balance)) if model.opening_balance else float('0'),
            closing_balance=float(str(model.closing_balance)) if model.closing_balance else float('0'),
            total_credits=float(str(model.total_credits)) if model.total_credits else float('0'),
            total_debits=float(str(model.total_debits)) if model.total_debits else float('0'),
            transaction_count=model.transaction_count or 0
        )