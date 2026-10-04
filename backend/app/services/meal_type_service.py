from app.repositories import meal_type_repository
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.meal_type import MealType
from app.schemas.meal_type import MealTypeCreate, MealTypeUpdate

def list(db: Session) -> list[MealType]:
    return meal_type_repository.get_all(db)

def get(db: Session, meal_id: int) -> MealType:
    item = meal_type_repository.get(db, meal_id)
    if not item:
        raise NotFoundError('Meal type not found')
    return item

def create(db: Session, data: MealTypeCreate) -> MealType:
    name = data.name.strip().upper()
    if meal_type_repository.get_by_name(db, name):
        raise ConflictError('Meal type already exists')
    return meal_type_repository.create(db, {'name': name, 'description': data.description})

def update(db: Session, meal_id: int, data: MealTypeUpdate) -> MealType:
    item = get(db, meal_id)
    values = data.model_dump(exclude_unset=True)
    if 'name' in values:
        name = values['name'].strip().upper()
        existing = meal_type_repository.get_by_name(db, name)
        if existing and existing.meal_id != meal_id:
            raise ConflictError('Meal type already exists')
        values['name'] = name
    return meal_type_repository.update(db, item, values)

def delete(db: Session, meal_id: int) -> None:
    item = get(db, meal_id)
    if item.schedules:
        raise BusinessRuleError('Cannot delete a meal type that already has schedules')
    meal_type_repository.delete(db, item)

list_meal_type = list
get_meal_type = get
create_meal_type = create
update_meal_type = update
delete_meal_type = delete
