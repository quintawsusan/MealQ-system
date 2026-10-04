from app.models.student_meal_response import StudentMealResponse
from sqlalchemy.orm import Session, joinedload


class StudentMealResponseRepository:
    def __init__(self):
        self.model = StudentMealResponse

    def get(self, db: Session, id: int):
        return db.get(StudentMealResponse, id)

    def get_all(self, db: Session):
        return db.query(StudentMealResponse).all()

    def create(self, db: Session, data: dict):
        item = StudentMealResponse(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(self, db: Session, db_obj: StudentMealResponse, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: StudentMealResponse):
        db.delete(db_obj)
        db.commit()
        return

    def get_for_student(self, db: Session, session_id: int, student_id: int):
        return db.query(StudentMealResponse).filter(StudentMealResponse.session_id == session_id, StudentMealResponse.student_id == student_id).first()

    def list_for_session(self, db: Session, session_id: int):
        return db.query(StudentMealResponse).options(joinedload(StudentMealResponse.student)).filter(StudentMealResponse.session_id == session_id).order_by(StudentMealResponse.student_id).all()

student_meal_response_repository = StudentMealResponseRepository()
