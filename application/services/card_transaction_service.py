from datetime import datetime, date
from typing import Dict, Any
from application.dtos.card_transaction_dtos import (
    CreateCardTransactionRequest,
    CardTransactionResponse,
    GetCardTransactionsRequest,
    GetCardTransactionsResponse,
    GetCardBalanceAtDateRequest,
    GetCardBalanceAtDateResponse,
    GetCardMonthlySummaryRequest,
    GetCardMonthlySummaryResponse,
    CardBalanceHistoryRequest,
    CardBalanceHistoryResponse,
    ExportTransactionsRequest,
    ExportTransactionsResponse,
    MonthlySummary
)
from core.use_cases.cards.record_card_transaction_use_case import RecordCardTransactionUseCase
from core.use_cases.cards.get_card_transactions_use_case import GetCardTransactionsUseCase
from core.use_cases.cards.get_card_balance_at_date_use_case import GetCardBalanceAtDateUseCase
from core.use_cases.cards.get_card_monthly_summary_use_case import GetCardMonthlySummaryUseCase
from core.use_cases.cards.export_card_transactions_use_case import ExportCardTransactionsUseCase
from core.use_cases.cards.generate_daily_snapshots_use_case import GenerateDailySnapshotsUseCase
import logging

logger = logging.getLogger(__name__)


class CardTransactionService:
    """
    Servicio para gestión de transacciones de tarjetas.
    
    Orquesta los casos de uso y proporciona una interfaz unificada
    para la trazabilidad de tarjetas.
    """
    
    def __init__(
        self,
        record_card_transaction_use_case: RecordCardTransactionUseCase,
        get_card_transactions_use_case: GetCardTransactionsUseCase,
        get_card_balance_at_date_use_case: GetCardBalanceAtDateUseCase,
        get_card_monthly_summary_use_case: GetCardMonthlySummaryUseCase,
        export_card_transactions_use_case: ExportCardTransactionsUseCase,
        generate_daily_snapshots_use_case: GenerateDailySnapshotsUseCase
    ):
        self.record_card_transaction_use_case = record_card_transaction_use_case
        self.get_card_transactions_use_case = get_card_transactions_use_case
        self.get_card_balance_at_date_use_case = get_card_balance_at_date_use_case
        self.get_card_monthly_summary_use_case = get_card_monthly_summary_use_case
        self.export_card_transactions_use_case = export_card_transactions_use_case
        self.generate_daily_snapshots_use_case = generate_daily_snapshots_use_case
    
    # ========== OPERACIONES BÁSICAS ==========
    
    def record_transaction(self, request: CreateCardTransactionRequest) -> CardTransactionResponse:
        """
        Registra una nueva transacción de tarjeta.
        
        Args:
            request: DTO con datos de la transacción
            
        Returns:
            CardTransactionResponse: Transacción registrada
        """
        try:
            transaction = self.record_card_transaction_use_case.execute(
                card_id=request.card_id,
                transaction_type=request.transaction_type,
                amount=request.amount,
                description=request.description,
                reference_id=request.reference_id,
                reference_type=request.reference_type
            )
            
            return self._transaction_to_response(transaction)
            
        except Exception as e:
            logger.error(f"Error al registrar transacción: {str(e)}")
            raise
    
    def get_transactions(self, request: GetCardTransactionsRequest) -> GetCardTransactionsResponse:
        """
        Obtiene transacciones de una tarjeta con filtros.
        
        Args:
            request: DTO con filtros de consulta
            
        Returns:
            GetCardTransactionsResponse: Transacciones y metadatos
        """
        try:
            result = self.get_card_transactions_use_case.execute(
                card_id=request.card_id,
                start_date=request.start_date,
                end_date=request.end_date,
                transaction_type=request.transaction_type,
                page=1,  
                page_size=100  
            )
            
            # Convertir entidades a DTOs de respuesta
            transactions_response = [
                self._transaction_to_response(t) for t in result['transactions']
            ]
            
            return GetCardTransactionsResponse(
                success=True,
                transactions=transactions_response,
                total_count=result['pagination']['total_count'],
                total_credits=result['summary']['total_credits'],
                total_debits=result['summary']['total_debits'],
                net_movement=result['summary']['net_movement']
            )
            
        except Exception as e:
            logger.error(f"Error al obtener transacciones: {str(e)}")
            return GetCardTransactionsResponse(
                success=False,
                transactions=[],
                total_count=0,
                total_credits=float('0'),
                total_debits=float('0'),
                net_movement=float('0'),
                message=str(e)
            )
    
    def get_balance_at_date(self, request: GetCardBalanceAtDateRequest) -> GetCardBalanceAtDateResponse:
        """
        Obtiene el balance de una tarjeta en una fecha específica.
        
        Args:
            request: DTO con fecha objetivo
            
        Returns:
            GetCardBalanceAtDateResponse: Balance histórico
        """
        try:
            balance = self.get_card_balance_at_date_use_case.execute(
                card_id=request.card_id,
                target_date=request.target_date
            )
            
            return GetCardBalanceAtDateResponse(
                success=True,
                card_id=request.card_id,
                target_date=request.target_date,
                balance_at_date=balance
            )
            
        except Exception as e:
            logger.error(f"Error al obtener balance histórico: {str(e)}")
            return GetCardBalanceAtDateResponse(
                success=False,
                card_id=request.card_id,
                target_date=request.target_date,
                balance_at_date=float('0'),
                message=str(e)
            )
    
    # ========== REPORTES Y RESÚMENES ==========
    
    def get_monthly_summary(self, request: GetCardMonthlySummaryRequest) -> GetCardMonthlySummaryResponse:
        """
        Obtiene resumen mensual o anual de una tarjeta.
        
        Args:
            request: DTO con año y mes opcional
            
        Returns:
            GetCardMonthlySummaryResponse: Resumen del período
        """
        try:
            result = self.get_card_monthly_summary_use_case.execute(
                card_id=request.card_id,
                year=request.year,
                month=request.month
            )
            
            if request.month:
                # Resumen mensual
                return GetCardMonthlySummaryResponse(
                    success=True,
                    card_id=request.card_id,
                    year=request.year,
                    monthly_summaries=[
                        MonthlySummary(
                            month=result['month'],
                            opening_balance=float('0'),  # No disponible en resumen básico
                            closing_balance=float('0'),  # No disponible en resumen básico
                            total_credits=result['total_credits'],
                            total_debits=result['total_debits'],
                            transaction_count=result['transaction_count'],
                            net_movement=result['net_movement']
                        )
                    ],
                    annual_totals={
                        'total_credits': result['total_credits'],
                        'total_debits': result['total_debits'],
                        'transaction_count': result['transaction_count'],
                        'net_movement': result['net_movement']
                    }
                )
            else:
                # Resumen anual
                monthly_summaries = [
                    MonthlySummary(
                        month=item['month'],
                        opening_balance=float('0'),
                        closing_balance=float('0'),
                        total_credits=item['total_credits'],
                        total_debits=item['total_debits'],
                        transaction_count=item['transaction_count'],
                        net_movement=item['net_movement']
                    )
                    for item in result['monthly_summaries']
                ]
                
                return GetCardMonthlySummaryResponse(
                    success=True,
                    card_id=request.card_id,
                    year=request.year,
                    monthly_summaries=monthly_summaries,
                    annual_totals=result['annual_totals']
                )
            
        except Exception as e:
            logger.error(f"Error al obtener resumen mensual: {str(e)}")
            return GetCardMonthlySummaryResponse(
                success=False,
                card_id=request.card_id,
                year=request.year,
                monthly_summaries=[],
                annual_totals={},
                message=str(e)
            )
    
    def get_balance_history(self, request: CardBalanceHistoryRequest) -> CardBalanceHistoryResponse:
        """
        Obtiene historial de balances diarios en un período.
        
        Args:
            request: DTO con período
            
        Returns:
            CardBalanceHistoryResponse: Historial de balances
        """
        try:
            # Generar lista de fechas en el período
            date_range = []
            current_date = request.start_date
            
            while current_date <= request.end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)
            
            # Obtener balance para cada fecha
            daily_balances = []
            total_movement = float('0')
            
            for current_date in date_range:
                try:
                    # Obtener balance al final del día
                    end_of_day = datetime.combine(current_date, datetime.max.time())
                    balance = self.get_card_balance_at_date_use_case.execute(
                        card_id=request.card_id,
                        target_date=end_of_day
                    )
                    
                    # Obtener transacciones del día para calcular movimiento
                    start_of_day = datetime.combine(current_date, datetime.min.time())
                    daily_transactions = self.get_card_transactions_use_case.execute(
                        card_id=request.card_id,
                        start_date=start_of_day,
                        end_date=end_of_day,
                        page=1,
                        page_size=1000  # Número alto para obtener todas
                    )
                    
                    daily_movement = daily_transactions['summary']['net_movement']
                    total_movement += daily_movement
                    
                    daily_balances.append({
                        'date': current_date,
                        'balance': balance,
                        'daily_movement': daily_movement,
                        'transaction_count': daily_transactions['pagination']['total_count']
                    })
                    
                except Exception as e:
                    logger.warning(f"Error procesando fecha {current_date}: {str(e)}")
                    continue
            
            # Calcular balances inicial y final
            opening_balance = float('0')
            closing_balance = float('0')
            
            if daily_balances:
                opening_balance = daily_balances[0]['balance'] - daily_balances[0]['daily_movement']
                closing_balance = daily_balances[-1]['balance']
            
            return CardBalanceHistoryResponse(
                success=True,
                card_id=request.card_id,
                period={'start': request.start_date, 'end': request.end_date},
                daily_balances=daily_balances,
                opening_balance=opening_balance,
                closing_balance=closing_balance,
                total_movement=total_movement
            )
            
        except Exception as e:
            logger.error(f"Error al obtener historial de balances: {str(e)}")
            return CardBalanceHistoryResponse(
                success=False,
                card_id=request.card_id,
                period={'start': request.start_date, 'end': request.end_date},
                daily_balances=[],
                opening_balance=float('0'),
                closing_balance=float('0'),
                total_movement=float('0'),
                message=str(e)
            )
    
    # ========== EXPORTACIÓN ==========
    
    def export_transactions(self, request: ExportTransactionsRequest) -> ExportTransactionsResponse:
        """
        Exporta transacciones a un archivo.
        
        Args:
            request: DTO con configuración de exportación
            
        Returns:
            ExportTransactionsResponse: Información del archivo generado
        """
        try:
            file_path = self.export_card_transactions_use_case.execute(
                card_id=request.card_id,
                start_date=request.start_date,
                end_date=request.end_date,
                export_format=request.export_format,
                include_summary=request.include_summary
            )
            
            # Obtener información del archivo
            import os
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Obtener conteo de transacciones
            transactions_result = self.get_card_transactions_use_case.execute(
                card_id=request.card_id,
                start_date=request.start_date,
                end_date=request.end_date,
                page=1,
                page_size=1  # Solo necesitamos el conteo
            )
            
            return ExportTransactionsResponse(
                success=True,
                file_path=file_path,
                file_size=file_size,
                transaction_count=transactions_result['pagination']['total_count']
            )
            
        except Exception as e:
            logger.error(f"Error al exportar transacciones: {str(e)}")
            return ExportTransactionsResponse(
                success=False,
                file_path='',
                file_size=0,
                transaction_count=0,
                message=str(e)
            )
    
    # ========== OPERACIONES DE MANTENIMIENTO ==========
    
    def generate_daily_snapshots(self, target_date: date = None) -> Dict[str, Any]:
        """
        Genera snapshots diarios para optimización.
        
        Args:
            target_date: Fecha para generar (default: ayer)
            
        Returns:
            Dict con estadísticas de la generación
        """
        try:
            return self.generate_daily_snapshots_use_case.execute(target_date)
            
        except Exception as e:
            logger.error(f"Error generando snapshots: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'date': target_date or date.today() - timedelta(days=1),
                'snapshots_created': 0,
                'errors': 1
            }
    
    def cleanup_old_snapshots(self, retention_days: int = 365) -> Dict[str, Any]:
        """
        Elimina snapshots antiguos.
        
        Args:
            retention_days: Días de retención
            
        Returns:
            Dict con estadísticas de la limpieza
        """
        try:
            return self.generate_daily_snapshots_use_case.cleanup_old_snapshots(retention_days)
            
        except Exception as e:
            logger.error(f"Error limpiando snapshots: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'snapshots_deleted': 0
            }
    
    # ========== MÉTODOS DE UTILIDAD ==========
    
    def _transaction_to_response(self, transaction) -> CardTransactionResponse:
        """Convierte una entidad de transacción a DTO de respuesta."""
        return CardTransactionResponse(
            id=transaction.id,
            card_id=transaction.card_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            previous_balance=transaction.previous_balance,
            new_balance=transaction.new_balance,
            operation_date=transaction.operation_date,
            recorded_at=transaction.recorded_at,
            description=transaction.notes,
            reference_id=transaction.diet_id or transaction.liquidation_id,
            reference_type='diet' if transaction.diet_id else 
                         'liquidation' if transaction.liquidation_id else None
        )