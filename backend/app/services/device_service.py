from app.repositories import device_repository, student_repository
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictError, NotFoundError
from app.models.device import StudentDevice
from app.schemas.device import DeviceCreate, DeviceUpdate

def get_for_student(db: Session, student_id: int) -> StudentDevice:
    device = device_repository.get_by_student_id(db, student_id)
    if not device:
        raise NotFoundError('Student device is not registered')
    return device

def register_for_student(db: Session, student_id: int, data: DeviceCreate) -> StudentDevice:
    student = student_repository.get(db, student_id)
    if not student:
        raise NotFoundError('Student not found')
    existing = device_repository.get_by_student_id(db, student_id)
    identifier_owner = device_repository.get_by_identifier(db, data.device_identifier)
    if identifier_owner and (not existing or identifier_owner.device_id != existing.device_id):
        raise ConflictError('This device identifier is already registered')
    if existing:
        return device_repository.update(db, existing, {'device_identifier': data.device_identifier, 'is_active': True})
    return device_repository.create(db, {'student_id': student_id, 'device_identifier': data.device_identifier, 'is_active': True})

def update_for_student(db: Session, student_id: int, data: DeviceUpdate) -> StudentDevice:
    device = get_for_student(db, student_id)
    values = data.model_dump(exclude_unset=True)
    if 'device_identifier' in values:
        owner = device_repository.get_by_identifier(db, values['device_identifier'])
        if owner and owner.device_id != device.device_id:
            raise ConflictError('This device identifier is already registered')
    return device_repository.update(db, device, values)

def delete_for_student(db: Session, student_id: int) -> None:
    device = get_for_student(db, student_id)
    device_repository.delete(db, device)

