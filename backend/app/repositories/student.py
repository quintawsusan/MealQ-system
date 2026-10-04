from app.models.student import Student
from app.models.user import User
from sqlalchemy.orm import Session


class StudentRepository:
    def __init__(self):
        self.model = Student

    def get(self, db: Session, id: int):
        return db.get(Student, id)

    def get_all(self, db: Session):
        return db.query(Student).all()

    def create(self, db: Session, data: dict):
        student = Student(**data)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    def update(self, db: Session, db_obj: Student, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Student):
        db.delete(db_obj)
        db.commit()
        return

    def get_by_user_id(self, db: Session, user_id: int):
        return db.query(Student).filter(Student.user_id == user_id).first()

    def get_by_student_number(self, db: Session, student_number: int):
        return db.query(Student).filter(Student.student_number == student_number).first()

    def list_active_ordered(self, db: Session, offset: int = 0, limit: int | None = None):
        query = db.query(Student).join(Student.user).filter(User.is_active.is_(True)).order_by(Student.student_number).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

student_repository = StudentRepository()
