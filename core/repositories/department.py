from abc import ABC, abstractmethod
from typing import Optional
from core.entities.department import Department

class DepartmentRepository(ABC):
    """
    Interfaz abstracta para el repositorio de departamentos.
    Define los métodos que cualquier implementación debe tener.
    """
    
    @abstractmethod
    def save(self, dpto: Department) -> Department:
        """Guarda un nuevo departamento en el repositorio"""
        pass

    @abstractmethod
    def get_by_id(self, dpto_id: int) -> Optional[Department]:
        """Obtiene un departamento por su ID"""
        pass

    @abstractmethod
    def get_all(self) -> list[Department]:
        """Obtiene todos los departamentos del sistema"""
        pass

    @abstractmethod
    def update(self, dpto: Department) -> Department:
        """Actualiza un departamento existente"""
        pass

    @abstractmethod
    def delete(self, dpto_id: int) -> bool:
        """Elimina un departamento por su ID"""
        pass