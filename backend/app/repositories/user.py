from app.models.user import User
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self):
        self.model = User

    def get(self, db: Session, id: int):
        return db.get(User, id)

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email.lower().strip()).first()

    def get_all(self, db: Session):
        return db.query(User).all()

    def list(self, db: Session, offset: int = 0, limit: int = 100):
        return db.query(User).offset(offset).limit(limit).all()

    def create(self, db: Session, data: dict):
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, db_obj: User, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: User):
        db.delete(db_obj)
        db.commit()
        return

user_repository = UserRepository()
