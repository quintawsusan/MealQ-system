from app.models.meal_session import MealSession
from app.models.meal_schedule import MealSchedule
from app.models.serving_batch import ServingBatch
from app.models.student_meal_response import StudentMealResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func


class MealSessionRepository:
    def __init__(self):
        self.model = MealSession

    def get(self, db: Session, id: int):
        return db.get(MealSession, id)

    def get_all(self, db: Session):
        return db.query(MealSession).all()

    def create(self, db: Session, data: dict):
        session = MealSession(**data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def update(self, db: Session, db_obj: MealSession, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: MealSession):
        db.delete(db_obj)
        db.commit()
        return

    def get_with_schedule(self, db: Session, session_id: int):
        return db.query(MealSession).options(joinedload(MealSession.schedule).joinedload(MealSchedule.meal_type)).filter(MealSession.session_id == session_id).first()

    def get_active_sessions(self, db: Session):
        return db.query(MealSession).filter(MealSession.status == "ACTIVE").all()

    def get_response_counts(self, db: Session, session_id: int):
        rows = db.query(StudentMealResponse.response, func.count(StudentMealResponse.response_id)).filter(StudentMealResponse.session_id == session_id).group_by(StudentMealResponse.response).all()
        return {response: count for response, count in rows}

    def batch_counts(self, db: Session, session_id: int):
        rows = db.query(ServingBatch.status, func.count(ServingBatch.batch_id)).filter(ServingBatch.session_id == session_id).group_by(ServingBatch.status).all()
        return {status: count for status, count in rows}

meal_session_repository = MealSessionRepository()
