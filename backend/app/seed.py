from sqlalchemy import select
from app.database import SessionLocal
from app.models.classroom import Classroom
from app.models.meal_type import MealType
DEFAULT_CLASSES=["Anita B","Ada Lab","Lovelace"]
DEFAULT_MEAL_TYPES=[("BREAKFAST","Morning meal"),("LUNCH","Midday meal"),("4PM SNACK","Afternoon snack"),("DINNER","Evening meal")]
def seed():
    db=SessionLocal()
    try:
        for name in DEFAULT_CLASSES:
            if not db.scalar(select(Classroom).where(Classroom.name==name)): db.add(Classroom(name=name))
        for name,description in DEFAULT_MEAL_TYPES:
            if not db.scalar(select(MealType).where(MealType.name==name)): db.add(MealType(name=name,description=description))
        db.commit(); print("Classes and meal types seeded successfully.")
    finally: db.close()
if __name__=="__main__": seed()
