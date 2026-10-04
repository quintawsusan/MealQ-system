from app.models.meal_schedule import MealSchedule
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_


class MealScheduleRepository:
    def __init__(self):
        self.model = MealSchedule

    def get(self, db: Session, id: int):
        return db.get(MealSchedule, id)

    def get_all(self, db: Session):
        return db.query(MealSchedule).all()

    def create(self, db: Session, data: dict):
        schedule = MealSchedule(**data)
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    def update(self, db: Session, db_obj: MealSchedule, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: MealSchedule):
        db.delete(db_obj)
        db.commit()
        return

    def get_with_type(self, db: Session, schedule_id: int):
        return db.query(MealSchedule).options(joinedload(MealSchedule.meal_type)).filter(MealSchedule.schedule_id == schedule_id).first()

    def list_range(self, db: Session, start_date, end_date, active_only: bool = False):
        query = db.query(MealSchedule).order_by(MealSchedule.meal_date, MealSchedule.start_time)
        if start_date:
            query = query.filter(MealSchedule.meal_date >= start_date)
        if end_date:
            query = query.filter(MealSchedule.meal_date <= end_date)
        if active_only:
            query = query.filter(MealSchedule.is_active.is_(True))
        return query.all()

    def has_duplicate(self, db: Session, meal_type_id: int, meal_date, start_time, exclude_id=None):
        query = db.query(MealSchedule.schedule_id).filter(
            MealSchedule.meal_type_id == meal_type_id,
            MealSchedule.meal_date == meal_date,
            MealSchedule.start_time == start_time,
        )
        if exclude_id:
            query = query.filter(MealSchedule.schedule_id != exclude_id)
        return query.first() is not None

meal_schedule_repository = MealScheduleRepository()
