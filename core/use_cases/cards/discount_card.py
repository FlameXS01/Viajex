from core.repositories.card_repository import CardRepository
from core.repositories.card_transaction_repository import CardTransactionRepository
from core.use_cases.cards.record_card_transaction_use_case import RecordCardTransactionUseCase

class DiscountCardUseCase:
    def __init__(self, card_repository: CardRepository, 
                card_transaction_repository: CardTransactionRepository 
    ):
        self.card_repository = card_repository
        self.card_transaction_repository = card_transaction_repository
        self.record_card_transaction = RecordCardTransactionUseCase( card_transaction_repository, card_repository,)

    def execute(self, card_id: int, amount: float) -> bool:
        # Verificar si la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            return False
        
        # Recargar la tarjeta
        succes = self.card_repository.discount(card_id, amount)
        if succes:
            self.record_card_transaction.execute(card_id, 'PAYMENT', -amount, description='Liquidación de dieta', reference_type='DEBIT' )
        
        return succes 