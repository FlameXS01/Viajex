from core.repositories.card_repository import CardRepository
from core.repositories.card_transaction_repository import CardTransactionRepository
from core.use_cases.cards.record_card_transaction_use_case import RecordCardTransactionUseCase

class RechargeCardUseCase:
    def __init__(self, card_repository: CardRepository, 
                card_transaction_repository: CardTransactionRepository, 
                is_refound: bool = False 
    ):
        self.card_repository = card_repository
        self.card_transaction_repository = card_transaction_repository, 
        self.is_refound = is_refound,
        self.record_card_transaction = RecordCardTransactionUseCase( card_transaction_repository, card_repository)

    def execute(self, card_id: int, amount: float) -> bool:
        # Verificar si la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            return False
        
        # Recargar la tarjeta
        succes = self.card_repository.recharge(card_id, amount)
        if succes:
            if not self.is_refound:
                self.record_card_transaction.execute(card_id, 'RECHARGE', amount, description='Recarga manual', reference_type='CREDIT')
            else:    
                self.record_card_transaction.execute(card_id, 'REFUND', amount, description='Reembolso de hospedaje', reference_type='CREDIT')
        
        return succes 