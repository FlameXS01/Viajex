from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.diet_service import DietService

class DietServiceRepository(ABC):
    """

    Interfaz para el repositorio de servicios de dieta.
    Define los contratos para las operaciones CRUD y consultas específicas.

    """
    
    @abstractmethod
    def create(self, diet_service: DietService) -> DietService:
        """
        
        Crea un nuevo servicio de dieta
        
        """
        pass
    
    @abstractmethod
    def get_by_id(self, diet_service_id: int) -> Optional[DietService]:
        """
        
        Obtiene un servicio de dieta por ID
        
        """
        pass
    
    @abstractmethod
    def get_by_local(self, is_local: bool) -> Optional[DietService]:
        """
        
        Obtiene el servicio de dieta por localidad (local/no local)
        
        """
        pass
    
    @abstractmethod
    def list_all(self) -> List[DietService]:
        """
        
        Lista todos los servicios de dieta
        
        """
        pass
    
    @abstractmethod
    def update(self, diet_service: DietService) -> DietService:
        """
        
        Actualiza un servicio de dieta existente
        
        """
        pass
    
    @abstractmethod
    def delete(self, diet_service_id: int) -> bool:
        """
        
        Elimina un servicio de dieta
        
        """
        pass