from __future__ import annotations
from app.repositories import meal_session_repository, serving_batch_repository, student_repository
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
KENYA_TIMEZONE = ZoneInfo("Africa/Nairobi")

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError, ValidationError
from app.models.meal_session import MealSession
from app.models.meal_schedule import MealSchedule
from app.models.serving_batch import ServingBatch
from app.models.student import Student
from app.models.student_batch import StudentBatch
from app.models.student_meal_response import StudentMealResponse
from app.schemas.meal_session import MealSessionCreate

def now() -> datetime:
    return datetime.now(timezone.utc)

def get(db: Session, session_id: int) -> MealSession:
    item = meal_session_repository.get_with_schedule(db, session_id)
    if not item:
        raise NotFoundError('Meal session not found')
    return item

def create(db: Session, data: MealSessionCreate, created_by: int) -> MealSession:
    if data.response_window > data.release_interval_seconds:
        raise ValidationError('response_window cannot exceed release_interval_seconds')
    schedule = db.get(MealSchedule, data.schedule_id)
    if not schedule:
        raise NotFoundError('Meal schedule not found')
    if not schedule.is_active:
        raise BusinessRuleError('Cannot create a session from an inactive schedule')
    existing = db.scalar(select(MealSession).where(MealSession.schedule_id == data.schedule_id))
    if existing:
        raise ConflictError('This schedule already has a meal session')
    session = meal_session_repository.create(db, {**data.model_dump(), 'created_by': created_by, 'status': 'SCHEDULED'})
    return session

def start(db: Session, session_id: int) -> MealSession:
    session = get(db, session_id)
    if session.status == 'COMPLETED':
        raise BusinessRuleError('Completed sessions cannot be restarted')
    if session.status == 'ACTIVE':
        return session
    session.status = 'ACTIVE'
    session.started_at = session.started_at or now()
    db.flush()
    if not session.batches:
        _generate_batches(db, session)
    _call_next_if_due(db, session, force_first=True)
    db.flush()
    return session

def pause(db: Session, session_id: int) -> MealSession:
    session = get(db, session_id)
    if session.status != 'ACTIVE':
        raise BusinessRuleError('Only an active session can be paused')
    session.status = 'PAUSED'
    db.flush()
    return session

def resume(db: Session, session_id: int) -> MealSession:
    session = get(db, session_id)
    if session.status != 'PAUSED':
        raise BusinessRuleError('Only a paused session can be resumed')
    session.status = 'ACTIVE'
    db.flush()
    _call_next_if_due(db, session, force_first=False)
    db.flush()
    return session

def complete(db: Session, session_id: int) -> MealSession:
    session = get(db, session_id)
    if session.status == 'COMPLETED':
        return session
    current_time = now()
    current = serving_batch_repository.get_current(db, session_id)
    if current:
        current.status = 'COMPLETED'
        current.completed_at = current_time
    session.status = 'COMPLETED'
    session.ended_at = current_time
    db.flush()
    return session

def delete(db, session_id):
    session = get(db, session_id)

    if session.status != "SCHEDULED":
        raise ValidationError("Only SCHEDULED meal sessions can be deleted")
    db.delete(session)
    db.flush()

def advance(db: Session, session_id: int, force: bool=False) -> ServingBatch | None:
    session = get(db, session_id)
    if session.status != 'ACTIVE':
        raise BusinessRuleError('Only active sessions can advance')
    batch = _advance_if_due(db, session, force=force)
    db.flush()
    return batch

def create_due_scheduled_sessions(db: Session) -> int:
    current_time_kenya = now().astimezone(KENYA_TIMEZONE)
    current_date = current_time_kenya.date()
    current_time = current_time_kenya.time()

    due_schedules = (
        db.query(MealSchedule)
        .filter(
            MealSchedule.is_active.is_(True),
            MealSchedule.meal_date == current_date,
            MealSchedule.start_time <= current_time,
        )
        .all()
    )

    created = 0

    for schedule in due_schedules:
        existing_session = db.scalar(
            select(MealSession).where(
                MealSession.schedule_id == schedule.schedule_id
            )
        )

        if existing_session:
            continue

        session = MealSession(
            schedule_id=schedule.schedule_id,
            status="SCHEDULED",
            batch_size=5,
            release_interval_seconds=180,
            response_window=60,
            created_by=schedule.created_by,
        )

        db.add(session)
        db.flush()

        start(db, session.session_id)
        created += 1
    return created

def start_due_scheduled_sessions(db: Session) -> int:
    current_time_kenya = now().astimezone(KENYA_TIMEZONE)
    current_date = current_time_kenya.date()
    current_time = current_time_kenya.time()
    scheduled_sessions = (
        db.query(MealSession)
        .join(MealSchedule, MealSession.schedule_id == MealSchedule.schedule_id)
        .filter(
            MealSession.status == "SCHEDULED",
            MealSchedule.is_active.is_(True),
            MealSchedule.meal_date == current_date,
            MealSchedule.start_time <= current_time,
        )
        .all()
    )

    started = 0
    for session in scheduled_sessions:
        start(db, session.session_id)
        started += 1
    return started

def worker_tick(db: Session) -> int:
    created = create_due_scheduled_sessions(db)
    started = start_due_scheduled_sessions(db)
    sessions = meal_session_repository.get_active_sessions(db)
    changed = created + started
    for session in sessions:
        batch = _advance_if_due(db, session, force=False)
        if batch:
            changed += 1
        db.flush()
    return changed

def _generate_batches(db: Session, session: MealSession) -> None:
    active_students = student_repository.list_active_ordered(db, limit=None)
    if not active_students:
        raise BusinessRuleError('Cannot start a meal session with no active students')
    for offset in range(0, len(active_students), session.batch_size):
        student_group = active_students[offset:offset + session.batch_size]
        batch = ServingBatch(session_id=session.session_id, batch_number=offset // session.batch_size + 1, status='WAITING')
        db.add(batch)
        db.flush()
        for position, student in enumerate(student_group, start=1):
            db.add(StudentBatch(batch_id=batch.batch_id, student_id=student.student_id, student_position=position))
            db.add(StudentMealResponse(session_id=session.session_id, student_id=student.student_id, batch_id=batch.batch_id, response='NO_RESPONSE', responded_at=None))
    db.flush()
    db.refresh(session)

def _call_next_if_due(db: Session, session: MealSession, force_first: bool) -> ServingBatch | None:
    current = serving_batch_repository.get_current(db, session.session_id)
    if current:
        return current
    next_batch = _get_next_waiting_batch(db, session.session_id)
    if not next_batch:
        complete(db, session.session_id)
        return None
    if force_first or _is_due_from_previous(db, session, next_batch):
        return _call_batch(db, next_batch)
    return None

def _advance_if_due(db: Session,session: MealSession,force: bool = False,) -> ServingBatch | None:
    current = serving_batch_repository.get_current(db, session.session_id)
    current_time = now()

    if current:
        if (
            force
            or _all_students_responded(
                db,
                session.session_id,
                current.batch_id,
            )
            or _response_window_expired(
                current,
                session.response_window,
                current_time,
            )
        ):
            current.status = 'COMPLETED'
            current.completed_at = current_time

            return _call_next_or_complete(
                db,
                session,
                current_time,
            )

        return current
    return _call_next_if_due(db,session,force_first=False,)

def _all_students_responded(db: Session,session_id: int,batch_id: int,) -> bool:
    pending = db.scalar(
        select(StudentMealResponse.student_id)
        .where(
            StudentMealResponse.session_id == session_id,
            StudentMealResponse.batch_id == batch_id,
            StudentMealResponse.response == 'NO_RESPONSE',
        )
        .limit(1)
    )

    return pending is None


def _response_window_expired(batch: ServingBatch,response_window_seconds: int,current_time: datetime,) -> bool:
    if not batch.called_at:
        return True

    called_at = batch.called_at

    if called_at.tzinfo is None:
        called_at = called_at.replace(tzinfo=timezone.utc)

    return current_time >= (
        called_at + timedelta(seconds=response_window_seconds)
    )
    return current_time >= (called_at + timedelta(seconds=response_window_seconds))

def _call_next_or_complete(db: Session, session: MealSession, now: datetime) -> ServingBatch | None:
    next_batch = _get_next_waiting_batch(db, session.session_id)
    if not next_batch:
        complete(db, session.session_id)
        return None
    return _call_batch(db, next_batch, now)

def _call_batch(db: Session, batch: ServingBatch, current_time: datetime | None=None) -> ServingBatch:
    batch.status = 'CALLED'
    batch.called_at = current_time or now()
    batch.completed_at = None
    db.flush()
    return batch

def _get_next_waiting_batch(db: Session, session_id: int) -> ServingBatch | None:
    stmt = select(ServingBatch).where(ServingBatch.session_id == session_id, ServingBatch.status == 'WAITING').order_by(ServingBatch.batch_number).limit(1)
    return db.scalar(stmt)

def _release_due(batch: ServingBatch, interval_seconds: int, now: datetime) -> bool:
    if not batch.called_at:
        return True
    called_at = batch.called_at
    if called_at.tzinfo is None:
        called_at = called_at.replace(tzinfo=timezone.utc)
    return now >= called_at + timedelta(seconds=interval_seconds)

def _is_due_from_previous(db: Session, session: MealSession, next_batch: ServingBatch) -> bool:
    previous = db.scalar(select(ServingBatch).where(ServingBatch.session_id == session.session_id, ServingBatch.batch_number == next_batch.batch_number - 1))
    if not previous or not previous.called_at:
        return True
    return _release_due(previous, session.release_interval_seconds, now())

def build_my_batch(db: Session, session_id: int, student_id: int) -> dict:
    session = get(db, session_id)
    batch = serving_batch_repository.get_by_student(db, session_id, student_id)
    if not batch:
        raise NotFoundError('Student is not assigned to this meal session')
    membership = next((member for member in batch.members if member.student_id == student_id)) if batch.members else None
    if membership is None:
        membership = db.scalar(select(StudentBatch).where(StudentBatch.batch_id == batch.batch_id, StudentBatch.student_id == student_id))
    response = db.scalar(select(StudentMealResponse).where(StudentMealResponse.session_id == session_id, StudentMealResponse.student_id == student_id))
    if not response or not membership:
        raise NotFoundError('Student batch response record not found')
    is_current = batch.status == 'CALLED'
    response_window_open = bool(is_current and batch.called_at and (now() <= batch.called_at + timedelta(seconds=session.response_window)))
    return {'session_id': session_id, 'batch_id': batch.batch_id, 'batch_number': batch.batch_number, 'batch_status': batch.status, 'student_id': student_id, 'student_number': membership.student.student_number if membership.student else db.get(Student, student_id).student_number, 'student_position': membership.student_position, 'response': response.response, 'responded_at': response.responded_at, 'is_currently_called': is_current, 'response_window_open': response_window_open}

def respond(db: Session, session_id: int, student_id: int, response_value: str) -> StudentMealResponse:
    session = get(db, session_id)
    if session.status != 'ACTIVE':
        raise BusinessRuleError('Responses can only be submitted while the meal session is active')
    response = db.scalar(select(StudentMealResponse).where(StudentMealResponse.session_id == session_id, StudentMealResponse.student_id == student_id))
    if not response:
        raise NotFoundError('Student is not assigned to this meal session')
    batch = db.get(ServingBatch, response.batch_id)
    if not batch or batch.status != 'CALLED':
        raise BusinessRuleError('Your batch is not currently being called')
    current_time = now()
    if batch.called_at:
        called_at = batch.called_at if batch.called_at.tzinfo else batch.called_at.replace(tzinfo=timezone.utc)
        if current_time > called_at + timedelta(seconds=session.response_window):
            raise BusinessRuleError('The response window for this batch has closed')
    if response.response != 'NO_RESPONSE' and response.response != response_value:
        raise BusinessRuleError('A response cannot be changed after submission')
    response.response = response_value
    response.responded_at = current_time
    db.flush()
    return response

get_session = get
create_session = create
start_session = start
pause_session = pause
resume_session = resume
complete_session = complete
advance_session = advance

def list_sessions(db: Session, offset: int = 0, limit: int = 100):
    return meal_session_repository.get_all(db)[offset:offset + limit]

def list_batches(db: Session, session_id: int):
    return serving_batch_repository.list_for_session(db, session_id)

def current_batch(db: Session, session_id: int):
    return serving_batch_repository.get_current(db, session_id)
