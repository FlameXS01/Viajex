from datetime import datetime, date, timedelta
from decimal import Decimal
from core.repositories.card_transaction_repository import CardTransactionRepository, CardBalanceSnapshotRepository
from core.repositories.card_repository import CardRepository
import logging

logger = logging.getLogger(__name__)


class GenerateDailySnapshotsUseCase:
    """
    Caso de uso para generar snapshots diarios de balances.
    
    Este caso de uso se ejecuta periódicamente (ej: cada noche) para
    precalcular balances diarios y optimizar consultas históricas.
    """
    
    def __init__(
        self,
        card_transaction_repository: CardTransactionRepository,
        card_balance_snapshot_repository: CardBalanceSnapshotRepository,
        card_repository: CardRepository
    ):
        self.card_transaction_repository = card_transaction_repository
        self.card_balance_snapshot_repository = card_balance_snapshot_repository
        self.card_repository = card_repository
    
    def execute(self, target_date: date = None, force_regenerate: bool = False) -> dict:
        """
        Genera snapshots para un día específico.
        
        Args:
            target_date: Fecha para generar snapshots (default: ayer)
            force_regenerate: Regenerar incluso si ya existe
            
        Returns:
            Dict con estadísticas de la generación
        """
        # Usar ayer si no se especifica fecha
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        logger.info(f"Iniciando generación de snapshots para {target_date}")
        
        # Obtener todas las tarjetas activas
        cards = self.card_repository.get_all()
        
        stats = {
            'date': target_date,
            'total_cards': len(cards),
            'snapshots_created': 0,
            'snapshots_updated': 0,
            'snapshots_skipped': 0,
            'errors': 0
        }
        
        for card in cards:
            try:
                # Verificar si ya existe snapshot para esta fecha
                existing_snapshot = self.card_balance_snapshot_repository.get_by_card_and_date(
                    card.card_id, target_date
                )
                
                if existing_snapshot and not force_regenerate:
                    stats['snapshots_skipped'] += 1
                    continue
                
                # Calcular snapshot
                snapshot = self._calculate_daily_snapshot(card.card_id, target_date)
                
                if snapshot:
                    # Guardar snapshot
                    saved_snapshot = self.card_balance_snapshot_repository.save(snapshot)
                    
                    if existing_snapshot:
                        stats['snapshots_updated'] += 1
                    else:
                        stats['snapshots_created'] += 1
                    
                    logger.debug(
                        f"Snapshot generado: Tarjeta={card.card_number}, "
                        f"Fecha={target_date}, "
                        f"Balance={saved_snapshot.closing_balance}"
                    )
                
            except Exception as e:
                stats['errors'] += 1
                logger.error(
                    f"Error generando snapshot para tarjeta {card.card_id}: {str(e)}"
                )
        
        logger.info(
            f"Generación de snapshots completada: "
            f"{stats['snapshots_created']} creados, "
            f"{stats['snapshots_updated']} actualizados, "
            f"{stats['snapshots_skipped']} omitidos, "
            f"{stats['errors']} errores"
        )
        
        return stats
    
    def _calculate_daily_snapshot(self, card_id: int, snapshot_date: date):
        """Calcula un snapshot diario para una tarjeta."""
        from core.entities.card_balance_snapshot import CardBalanceSnapshot
        
        # Calcular inicio y fin del día
        start_of_day = datetime.combine(snapshot_date, datetime.min.time())
        end_of_day = datetime.combine(snapshot_date, datetime.max.time())
        
        # Obtener balance al inicio del día
        opening_balance = self.card_transaction_repository.get_balance_at_date(
            card_id, start_of_day
        )
        
        # Obtener transacciones del día
        transactions = self.card_transaction_repository.get_by_card_id(
            card_id=card_id,
            start_date=start_of_day,
            end_date=end_of_day
        )
        
        # Calcular totales
        total_credits = Decimal('0')
        total_debits = Decimal('0')
        
        for transaction in transactions:
            if transaction.amount > 0:
                total_credits += transaction.amount
            else:
                total_debits += abs(transaction.amount)
        
        # Calcular balance de cierre
        closing_balance = opening_balance + total_credits - total_debits
        
        # Crear snapshot
        return CardBalanceSnapshot(
            card_id=card_id,
            snapshot_date=snapshot_date,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            total_credits=total_credits,
            total_debits=total_debits,
            transaction_count=len(transactions)
        )
    
    def cleanup_old_snapshots(self, retention_days: int = 365) -> dict:
        """
        Elimina snapshots antiguos para mantenimiento.
        
        Args:
            retention_days: Días de retención (snapshots más antiguos se eliminan)
            
        Returns:
            Dict con estadísticas de la limpieza
        """
        cutoff_date = date.today() - timedelta(days=retention_days)
        
        deleted_count = self.card_balance_snapshot_repository.delete_snapshots_before_date(
            cutoff_date
        )
        
        stats = {
            'cutoff_date': cutoff_date,
            'snapshots_deleted': deleted_count
        }
        
        logger.info(
            f"Limpieza de snapshots completada: "
            f"{deleted_count} snapshots anteriores a {cutoff_date} eliminados"
        )
        
        return stats