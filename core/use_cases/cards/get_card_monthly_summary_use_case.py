from typing import Dict, Any, Optional
from core.repositories.card_transaction_repository import CardTransactionRepository, CardBalanceSnapshotRepository
from core.repositories.card_repository import CardRepository


class GetCardMonthlySummaryUseCase:
    """
    Caso de uso para obtener resumen mensual/anual de una tarjeta.
    
    Utiliza snapshots precalculados para mejor rendimiento.
    """
    
    def __init__(
        self,
        card_balance_snapshot_repository: CardBalanceSnapshotRepository,
        card_transaction_repository: CardTransactionRepository,
        card_repository: CardRepository
    ):
        self.card_balance_snapshot_repository = card_balance_snapshot_repository
        self.card_transaction_repository = card_transaction_repository
        self.card_repository = card_repository
    
    def execute(self, card_id: int, year: int, month: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene resumen mensual o anual de una tarjeta.
        
        Args:
            card_id: ID de la tarjeta
            year: Año del resumen
            month: Mes (1-12) o None para resumen anual
            
        Returns:
            Dict con el resumen del período
            
        Raises:
            ValueError: Si las validaciones fallan
        """
        # Validaciones
        if not card_id or card_id <= 0:
            raise ValueError("El ID de la tarjeta debe ser un número positivo")
        
        if year < 2000 or year > 2100:
            raise ValueError("El año debe estar entre 2000 y 2100")
        
        if month is not None and (month < 1 or month > 12):
            raise ValueError("El mes debe estar entre 1 y 12")
        
        # Verificar que la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Tarjeta con ID {card_id} no encontrada")
        
        # Obtener resumen desde snapshots (más rápido)
        snapshot_summary = self.card_balance_snapshot_repository.get_monthly_summary(
            card_id, year, month
        )
        
        if not snapshot_summary and month:
            # Si no hay snapshot para ese mes, calcular manualmente
            return self._calculate_monthly_summary_manually(card_id, year, month)
        elif not snapshot_summary:
            # Si no hay snapshots para el año, calcular manualmente
            return self._calculate_annual_summary_manually(card_id, year)
        
        return snapshot_summary
    
    def _calculate_monthly_summary_manually(self, card_id: int, year: int, month: int) -> Dict[str, Any]:
        """Calcula resumen mensual manualmente cuando no hay snapshots."""
        from datetime import datetime, timedelta
        
        # Calcular fechas del mes
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Obtener resumen del período
        summary = self.card_transaction_repository.get_summary_by_card_and_period(
            card_id, start_date, end_date
        )
        
        return {
            'month': month,
            'total_credits': summary.get('total_credits', float('0')),
            'total_debits': summary.get('total_debits', float('0')),
            'transaction_count': summary.get('transaction_count', 0),
            'net_movement': summary.get('net_movement', float('0'))
        }
    
    def _calculate_annual_summary_manually(self, card_id: int, year: int) -> Dict[str, Any]:
        """Calcula resumen anual manualmente cuando no hay snapshots."""
        monthly_summaries = []
        annual_totals = {
            'total_credits': float('0'),
            'total_debits': float('0'),
            'transaction_count': 0
        }
        
        # Calcular mes por mes
        for month in range(1, 13):
            month_summary = self._calculate_monthly_summary_manually(card_id, year, month)
            
            monthly_summaries.append({
                'month': month,
                'total_credits': month_summary['total_credits'],
                'total_debits': month_summary['total_debits'],
                'transaction_count': month_summary['transaction_count'],
                'net_movement': month_summary['net_movement']
            })
            
            annual_totals['total_credits'] += month_summary['total_credits']
            annual_totals['total_debits'] += month_summary['total_debits']
            annual_totals['transaction_count'] += month_summary['transaction_count']
        
        annual_totals['net_movement'] = (
            annual_totals['total_credits'] - annual_totals['total_debits']
        )
        
        return {
            'year': year,
            'monthly_summaries': monthly_summaries,
            'annual_totals': annual_totals
        }