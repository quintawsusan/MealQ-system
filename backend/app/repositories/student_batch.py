from app.models.student_batch import StudentBatch
from sqlalchemy.orm import Session


class StudentBatchRepository:
    def __init__(self):
        self.model = StudentBatch

    def get(self, db: Session, id: int):
        return db.get(StudentBatch, id)

    def get_all(self, db: Session):
        return db.query(StudentBatch).all()

    def create(self, db: Session, data: dict):
        item = StudentBatch(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(self, db: Session, db_obj: StudentBatch, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: StudentBatch):
        db.delete(db_obj)
        db.commit()
        return

    def get_membership(self, db: Session, batch_id: int, student_id: int):
        return db.query(StudentBatch).filter(StudentBatch.batch_id == batch_id, StudentBatch.student_id == student_id).first()

student_batch_repository = StudentBatchRepository()
