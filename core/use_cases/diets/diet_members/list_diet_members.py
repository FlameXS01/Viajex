from typing import List
from core.entities.diet_member import DietMember
from core.repositories.diet_member_repository import DietMemberRepository

class ListDietMembersUseCase:
    """Caso de uso para listar miembros de una dieta grupal"""
    
    def __init__(self, diet_member_repository: DietMemberRepository):
        self.diet_member_repository = diet_member_repository
    
    def execute(self, diet_id: int) -> List[DietMember]:
        return self.diet_member_repository.list_by_diet(diet_id)