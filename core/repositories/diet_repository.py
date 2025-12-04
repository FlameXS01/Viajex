from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from core.entities.diet import Diet, DietStatus

class DietRepository(ABC):
    """

    Interfaz para el repositorio de dietas (anticipos).
    Define los contratos para las operaciones CRUD y consultas específicas.

    """
    
    @abstractmethod
    def create(self, diet: Diet) -> Diet:
        """
        
        Crea una nueva dieta (anticipo)
        
        """
        pass
    
    @abstractmethod
    def get_by_id(self, diet_id: int) -> Optional[Diet]:
        """
        
        Obtiene una dieta por ID
        
        """
        pass
    
    @abstractmethod
    def get_all(self) -> list[Diet]:
        """
        
        Obtiene una lista de todas las dietas
        
        """
        pass


    @abstractmethod
    def get_by_advance_number(self, advance_number: int) -> Optional[Diet]:
        """
        
        Obtiene una dieta por número de anticipo
        
        """
        pass
    
    @abstractmethod
    def list_by_status(self, status: str) -> List[Diet]:
        """
        
        Lista dietas por estado
        
        """
        pass
    
    @abstractmethod
    def list_by_request_user(self, request_user_id: int) -> List[Diet]:
        """
        
        Lista dietas por solicitante
        
        """
        pass
    
    @abstractmethod
    def list_by_date_range(self, start_date: date, end_date: date) -> List[Diet]:
        """
        
        Lista dietas por rango de fechas
        
        """
        pass
    
    @abstractmethod
    def list_pending_liquidation(self) -> List[Diet]:
        """
        
        Lista dietas pendientes de liquidación (REQUESTED)
        
        """
        pass
    
    @abstractmethod
    def update(self, diet: Diet) -> Diet:
        """
        
        Actualiza una dieta existente
        
        """
        pass

    @abstractmethod
    def update_status(self,id: int, status: str) -> Optional[Diet]:
        """
        
        Actualiza una dieta existente con otro status
        
        """
        pass
    
    @abstractmethod
    def delete(self, diet_id: int) -> bool:
        """
        
        Elimina una dieta
        
        """
        pass
    
    @abstractmethod
    def get_last_advance_number(self) -> int:
        """
        
        Obtiene el último número de anticipo utilizado
        
        """
        pass
    
    @abstractmethod
    def reset_advance_numbers(self) -> bool:
        """
        
        Reinicia la secuencia de números de anticipo a 1
        
        """
        pass