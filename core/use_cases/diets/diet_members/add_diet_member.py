from core.entities.diet_member import DietMember
from core.repositories.diet_repository import DietRepository
from core.repositories.diet_member_repository import DietMemberRepository
from core.repositories.request_user_repository import RequestUserRepository

class AddDietMemberUseCase:
    """Caso de uso para agregar un miembro a una dieta grupal"""
    
    def __init__(
        self,
        diet_repository: DietRepository,
        diet_member_repository: DietMemberRepository,
        request_user_repository: RequestUserRepository
    ):
        self.diet_repository = diet_repository
        self.diet_member_repository = diet_member_repository
        self.request_user_repository = request_user_repository
    
    def execute(self, diet_id: int, request_user_id: int) -> DietMember:
        # Validar que la dieta existe y es grupal
        diet = self.diet_repository.get_by_id(diet_id)
        if not diet:
            raise ValueError("La dieta no existe")
        
        # Validar que el solicitante existe
        request_user = self.request_user_repository.get_by_id(request_user_id)
        if not request_user:
            raise ValueError("El solicitante no existe")
        
        # Validar que no sea ya miembro
        if self.diet_member_repository.is_member_in_diet(diet_id, request_user_id):
            raise ValueError("El solicitante ya es miembro de esta dieta")
        
        # Crear el miembro
        diet_member = DietMember(
            diet_id=diet_id,
            request_user_id=request_user_id
        )
        
        return self.diet_member_repository.create(diet_member)