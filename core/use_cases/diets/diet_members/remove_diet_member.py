from core.repositories.diet_member_repository import DietMemberRepository

class RemoveDietMemberUseCase:
    """Caso de uso para eliminar un miembro de una dieta grupal"""
    
    def __init__(self, diet_member_repository: DietMemberRepository):
        self.diet_member_repository = diet_member_repository
    
    def execute(self, member_id: int) -> bool:
        return self.diet_member_repository.delete(member_id)