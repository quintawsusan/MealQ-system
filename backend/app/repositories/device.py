from app.models.device import StudentDevice
from sqlalchemy.orm import Session


class DeviceRepository:
    def __init__(self):
        self.model = StudentDevice

    def get(self, db: Session, id: int):
        return db.get(StudentDevice, id)

    def get_all(self, db: Session):
        return db.query(StudentDevice).all()

    def create(self, db: Session, data: dict):
        device = StudentDevice(**data)
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    def update(self, db: Session, db_obj: StudentDevice, data: dict):
        for key, value in data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: StudentDevice):
        db.delete(db_obj)
        db.commit()
        return

    def get_by_student_id(self, db: Session, student_id: int):
        return db.query(StudentDevice).filter(StudentDevice.student_id == student_id).first()

    def get_by_identifier(self, db: Session, identifier: str):
        return db.query(StudentDevice).filter(StudentDevice.device_identifier == identifier).first()

device_repository = DeviceRepository()
