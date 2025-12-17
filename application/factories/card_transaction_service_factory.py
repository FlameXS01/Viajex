from infrastructure.database.session import SessionLocal, get_db
from infrastructure.database.repositories.card_repository import CardRepositoryImpl
from infrastructure.database.repositories.card_transaction_repository import (
    CardTransactionRepositoryImpl,
    CardBalanceSnapshotRepositoryImpl
)
from core.use_cases.cards.record_card_transaction_use_case import RecordCardTransactionUseCase
from core.use_cases.cards.get_card_transactions_use_case import GetCardTransactionsUseCase
from core.use_cases.cards.get_card_balance_at_date_use_case import GetCardBalanceAtDateUseCase
from core.use_cases.cards.get_card_monthly_summary_use_case import GetCardMonthlySummaryUseCase
from core.use_cases.cards.export_card_transactions_use_case import ExportCardTransactionsUseCase
from core.use_cases.cards.generate_daily_snapshots_use_case import GenerateDailySnapshotsUseCase
from application.services.card_transaction_service import CardTransactionService


class CardTransactionServiceFactory:
    """
    Factory para crear instancias de CardTransactionService con todas sus dependencias.
    
    Simplifica la inyección de dependencias y garantiza que todos los
    casos de uso tengan los repositorios correctos.
    """
    @staticmethod
    def create() -> CardTransactionService:
        """
        Crea una instancia completa de CardTransactionService.
        
        Returns:
            CardTransactionService: Servicio configurado y listo para usar
        """
        # Obtener sesión de base de datos
        db = SessionLocal()
        
        
        # Crear repositorios
        card_repository = CardRepositoryImpl(db)
        card_transaction_repository = CardTransactionRepositoryImpl(db)
        card_balance_snapshot_repository = CardBalanceSnapshotRepositoryImpl(db)
        
        # Crear casos de uso
        record_card_transaction_use_case = RecordCardTransactionUseCase(
            card_transaction_repository=card_transaction_repository,
            card_repository=card_repository
        )
        
        get_card_transactions_use_case = GetCardTransactionsUseCase(
            card_transaction_repository=card_transaction_repository,
            card_repository=card_repository
        )
        
        get_card_balance_at_date_use_case = GetCardBalanceAtDateUseCase(
            card_transaction_repository=card_transaction_repository,
            card_repository=card_repository
        )
        
        get_card_monthly_summary_use_case = GetCardMonthlySummaryUseCase(
            card_balance_snapshot_repository=card_balance_snapshot_repository,
            card_transaction_repository=card_transaction_repository,
            card_repository=card_repository
        )
        
        export_card_transactions_use_case = ExportCardTransactionsUseCase(
            card_transaction_repository=card_transaction_repository,
            card_repository=card_repository
        )
        
        generate_daily_snapshots_use_case = GenerateDailySnapshotsUseCase(
            card_transaction_repository=card_transaction_repository,
            card_balance_snapshot_repository=card_balance_snapshot_repository,
            card_repository=card_repository
        )
        
        # Crear y retornar servicio
        return CardTransactionService(
            record_card_transaction_use_case=record_card_transaction_use_case,
            get_card_transactions_use_case=get_card_transactions_use_case,
            get_card_balance_at_date_use_case=get_card_balance_at_date_use_case,
            get_card_monthly_summary_use_case=get_card_monthly_summary_use_case,
            export_card_transactions_use_case=export_card_transactions_use_case,
            generate_daily_snapshots_use_case=generate_daily_snapshots_use_case
        )