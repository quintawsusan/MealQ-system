from app.models.meal_type import MealType
from sqlalchemy.orm import Session


class MealTypeRepository:
    def __init__(self):
        self.model = MealType

    def get(self, db: Session, id: int):
        return db.get(MealType, id)

    def get_all(self, db: Session):
        return db.query(MealType).all()

    def create(self, db: Session, data: dict):
        meal_type = MealType(**data)
        db.add(meal_type)
        db.commit()
        db.refresh(meal_type)
        return meal_type

    def update(self, db: Session, db_obj: MealType, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: MealType):
        db.delete(db_obj)
        db.commit()
        return

    def get_by_name(self, db: Session, name: str):
        return db.query(MealType).filter(MealType.name == name.strip().upper()).first()

meal_type_repository = MealTypeRepository()
