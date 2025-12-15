from sqlalchemy.orm import Session
from core.entities.department import Department
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from core.repositories.department_repository import DepartmentRepository
from infrastructure.database.models import DepartmentModel

class DepartmentRepositoryImpl(DepartmentRepository):
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, dpto: Department) -> Department:
        try:
            db_department = DepartmentModel(
                name=dpto.name
            )
            self.db.add(db_department)
            self.db.commit()
            self.db.refresh(db_department)
            return self._to_entity(db_department)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al guardar departamento: {str(e)}")

    def get_by_id(self, dpto_id: int) -> Department:
        try:
            db_department = self.db.query(DepartmentModel).filter(DepartmentModel.id == dpto_id).first()
            return self._to_entity(db_department) if db_department else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener departamento: {str(e)}")

    def get_by_name(self, name: str) -> Department:
        try:
            db_department = self.db.query(DepartmentModel).filter(
                DepartmentModel.name == name
            ).first()
            return self._to_entity(db_department) if db_department else None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener departamento por nombre: {str(e)}")

    def get_all(self) -> list[Department]:
        try:
            db_departments = self.db.query(DepartmentModel).order_by(
                DepartmentModel.name.asc()
            ).all()
            return [self._to_entity(dept) for dept in db_departments]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener todos los departamentos: {str(e)}")

    def update(self, dpto: Department) -> Department:
        try:
            db_department = self.db.query(DepartmentModel).filter(
                DepartmentModel.id == dpto.id
            ).first()
            if db_department:
                db_department.name = dpto.name
                self.db.commit()
                self.db.refresh(db_department)
            return self._to_entity(db_department)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar departamento: {str(e)}")

    def delete(self, dpto_id: int) -> bool:
        try:
            db_department = self.db.query(DepartmentModel).filter(DepartmentModel.id == dpto_id).first()
            if db_department:
                self.db.delete(db_department)
                self.db.commit()
                return True
            return False
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Error de integridad al eliminar departamento: {str(e)}")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error de base de datos al eliminar departamento: {str(e)}")

    def _to_entity(self, db_department: DepartmentModel) -> Department:
        return Department(
            id=db_department.id,
            name=db_department.name
        )