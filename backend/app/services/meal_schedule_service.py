from app.repositories import meal_schedule_repository, meal_type_repository
from datetime import date
from sqlalchemy.orm import Session
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError, ValidationError
from app.models.meal_schedule import MealSchedule
from app.schemas.meal_schedule import MealScheduleCreate, MealScheduleUpdate

def get(db: Session, schedule_id: int) -> MealSchedule:
    item = meal_schedule_repository.get_with_type(db, schedule_id)
    if not item:
        raise NotFoundError('Meal schedule not found')
    return item

def list(db: Session, start_date: date | None, end_date: date | None, active_only: bool) -> list[MealSchedule]:
    if start_date and end_date and (end_date < start_date):
        raise ValidationError('end_date cannot be before start_date')
    return meal_schedule_repository.list_range(db, start_date, end_date, active_only)

def create(db: Session, data: MealScheduleCreate, created_by: int) -> MealSchedule:
    if data.end_time <= data.start_time:
        raise ValidationError('end_time must be later than start_time')
    if not meal_type_repository.get(db, data.meal_type_id):
        raise NotFoundError('Meal type not found')
    if meal_schedule_repository.has_duplicate(db, data.meal_type_id, data.meal_date, data.start_time):
        raise ConflictError('A schedule for this meal type/date/start time already exists')
    return meal_schedule_repository.create(db, {**data.model_dump(), 'created_by': created_by})

def update(db: Session, schedule_id: int, data: MealScheduleUpdate) -> MealSchedule:
    item = get(db, schedule_id)
    values = data.model_dump(exclude_unset=True)
    merged = {'meal_type_id': values.get('meal_type_id', item.meal_type_id), 'meal_date': values.get('meal_date', item.meal_date), 'start_time': values.get('start_time', item.start_time), 'end_time': values.get('end_time', item.end_time)}
    if merged['end_time'] <= merged['start_time']:
        raise ValidationError('end_time must be later than start_time')
    if not meal_type_repository.get(db, merged['meal_type_id']):
        raise NotFoundError('Meal type not found')
    if meal_schedule_repository.has_duplicate(db, merged['meal_type_id'], merged['meal_date'], merged['start_time'], schedule_id):
        raise ConflictError('Another schedule already uses that meal type/date/start time')
    return meal_schedule_repository.update(db, item, values)

def deactivate(db: Session, schedule_id: int) -> MealSchedule:
    item = get(db, schedule_id)
    return meal_schedule_repository.update(db, item, {'is_active': False})

get_schedule = get
list_schedule = list
create_schedule = create
update_schedule = update
deactivate_schedule = deactivate
