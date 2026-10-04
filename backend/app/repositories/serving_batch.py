from app.models.serving_batch import ServingBatch
from app.models.student_batch import StudentBatch
from sqlalchemy.orm import Session, joinedload


class ServingBatchRepository:
    def __init__(self):
        self.model = ServingBatch

    def get(self, db: Session, id: int):
        return db.get(ServingBatch, id)

    def get_all(self, db: Session):
        return db.query(ServingBatch).all()

    def create(self, db: Session, data: dict):
        batch = ServingBatch(**data)
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch

    def update(self, db: Session, db_obj: ServingBatch, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: ServingBatch):
        db.delete(db_obj)
        db.commit()
        return

    def list_for_session(self, db: Session, session_id: int):
        return db.query(ServingBatch).options(
            joinedload(ServingBatch.members).joinedload(StudentBatch.student),
            joinedload(ServingBatch.responses),
        ).filter(ServingBatch.session_id == session_id).order_by(ServingBatch.batch_number).all()

    def get_current(self, db: Session, session_id: int):
        return db.query(ServingBatch).options(
            joinedload(ServingBatch.members).joinedload(StudentBatch.student),
            joinedload(ServingBatch.responses),
        ).filter(
            ServingBatch.session_id == session_id,
            ServingBatch.status == "CALLED",
        ).order_by(ServingBatch.batch_number).first()

    def get_by_student(self, db: Session, session_id: int, student_id: int):
        return db.query(ServingBatch).join(ServingBatch.members).filter(
            ServingBatch.session_id == session_id,
            StudentBatch.student_id == student_id,
        ).first()

serving_batch_repository = ServingBatchRepository()
