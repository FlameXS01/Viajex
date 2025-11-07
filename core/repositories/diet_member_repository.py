from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.diet_member import DietMember

class DietMemberRepository(ABC):
    """

    Interfaz para el repositorio de miembros de dieta grupal.
    Define los contratos para las operaciones CRUD y consultas específicas.

    """
    
    @abstractmethod
    def create(self, diet_member: DietMember) -> DietMember:
        """
        
        Agrega un miembro a una dieta grupal
        
        """
        pass
    
    @abstractmethod
    def get_by_id(self, member_id: int) -> Optional[DietMember]:
        """
        
        Obtiene un miembro por ID
        
        """
        pass
    
    @abstractmethod
    def list_by_diet(self, diet_id: int) -> List[DietMember]:
        """
        
        Lista todos los miembros de una dieta grupal
        
        """
        pass
    
    @abstractmethod
    def list_by_request_user(self, request_user_id: int) -> List[DietMember]:
        """
        
        Lista todas las dietas grupales de un solicitante
        
        """
        pass
    
    @abstractmethod
    def delete(self, member_id: int) -> bool:
        """
        
        Elimina un miembro de una dieta grupal
        
        """
        pass
    
    @abstractmethod
    def delete_by_diet(self, diet_id: int) -> bool:
        """
        
        Elimina todos los miembros de una dieta grupal
        
        """
        pass
    
    @abstractmethod
    def is_member_in_diet(self, diet_id: int, request_user_id: int) -> bool:
        """
        
        Verifica si un solicitante ya es miembro de una dieta
        
        """
        pass