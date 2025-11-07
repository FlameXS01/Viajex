from sqlalchemy.orm import Session
from core.entities.department import Department
from core.repositories.department_repository import DepartmentRepository
from infrastructure.database.models import DepartmentModel

class DepartmentRepositoryImpl(DepartmentRepository):
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, dpto: Department) -> Department:
        db_department = DepartmentModel(
            name=dpto.name
        )
        self.db.add(db_department)
        self.db.commit()
        self.db.refresh(db_department)
        return self._to_entity(db_department)

    def get_by_id(self, dpto_id: int) -> Department:
        db_department = self.db.query(DepartmentModel).filter(DepartmentModel.id == dpto_id).first()
        return self._to_entity(db_department) if db_department else None

    def get_by_name(self, name: str) -> Department:
        db_department = self.db.query(DepartmentModel).filter(DepartmentModel.name == name).first()
        return self._to_entity(db_department) if db_department else None

    def get_all(self) -> list[Department]:
        db_departments = self.db.query(DepartmentModel).all()
        return [self._to_entity(dept) for dept in db_departments]

    def update(self, dpto: Department) -> Department:
        db_department = self.db.query(DepartmentModel).filter(DepartmentModel.id == dpto.id).first()
        if db_department:
            db_department.name = dpto.name
            self.db.commit()
            self.db.refresh(db_department)
        return self._to_entity(db_department)

    def delete(self, dpto_id: int) -> bool:
        db_department = self.db.query(DepartmentModel).filter(DepartmentModel.id == dpto_id).first()
        if db_department:
            self.db.delete(db_department)
            self.db.commit()
            return True
        return False

    def _to_entity(self, db_department: DepartmentModel) -> Department:
        return Department(
            id=db_department.id,
            name=db_department.name
        )