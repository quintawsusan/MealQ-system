from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin, require_student
from app.models.serving_batch import ServingBatch
from app.models.user import User
from app.schemas.meal_session import BatchResponse, MealSessionCreate, MealSessionResponse, MyBatchResponse, SessionMonitorResponse
from app.services import monitor_service
from app.services import student_service
from app.services import session_flow_service

router = APIRouter(prefix="/meal-sessions", tags=["Meal Sessions"])

@router.get("/active", response_model=MealSessionResponse | None)
def get_active_session(_: User = Depends(require_student),
    db: Session = Depends(get_db),):
    sessions = session_flow_service.list_sessions(db, offset=0, limit=500)
    active = next((session for session in sessions if session.status == "ACTIVE"), None)
    return active

def batch_to_response(batch: ServingBatch | None) -> BatchResponse | None:
    if batch is None:
        return None
    response_by_student = {response.student_id: response.response for response in batch.responses}
    members = [
        {
            "student_id": membership.student_id,
            "student_number": membership.student.student_number if membership.student else 0,
            "student_position": membership.student_position,
            "response": response_by_student.get(membership.student_id, "NO_RESPONSE"),
        }
        for membership in batch.members
    ]
    return BatchResponse(
        batch_id=batch.batch_id,
        session_id=batch.session_id,
        batch_number=batch.batch_number,
        status=batch.status,
        called_at=batch.called_at,
        completed_at=batch.completed_at,
        members=members,
    )


@router.get("", response_model=list[MealSessionResponse])
def list_sessions(
    status_filter: str | None = Query(default=None, alias="status"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    sessions = session_flow_service.list_sessions(db, offset=0, limit=500)
    if status_filter:
        sessions = [item for item in sessions if item.status == status_filter.upper()]
    return sessions


@router.post("", response_model=MealSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(data: MealSessionCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = session_flow_service.create_session(db, data, current_user.user_id)
    db.commit()
    return item

@router.get("/{session_id}", response_model=MealSessionResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    return session_flow_service.get_session(db, session_id)

@router.delete("/{session_id}")
def delete_meal_session(session_id: UUID,db: Session = Depends(get_db),_: User = Depends(require_admin),):
    session_flow_service.delete(db, session_id)
    db.commit()
    return {"message": "Meal session deleted successfully"}

@router.post("/{session_id}/start", response_model=MealSessionResponse)
def start_session(session_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = session_flow_service.start_session(db, session_id)
    db.commit()
    return item


@router.post("/{session_id}/pause", response_model=MealSessionResponse)
def pause_session(session_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = session_flow_service.pause_session(db, session_id)
    db.commit()
    return item


@router.post("/{session_id}/resume", response_model=MealSessionResponse)
def resume_session(session_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = session_flow_service.resume_session(db, session_id)
    db.commit()
    return item


@router.post("/{session_id}/complete", response_model=MealSessionResponse)
def complete_session(session_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = session_flow_service.complete_session(db, session_id)
    db.commit()
    return item


@router.post("/{session_id}/advance", response_model=BatchResponse | None)
def advance_session(
    session_id: UUID,
    force: bool = Query(default=False),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    batch = session_flow_service.advance_session(db, session_id, force=force)
    db.commit()
    return batch_to_response(batch)


@router.get("/{session_id}/batches", response_model=list[BatchResponse])
def list_batches(session_id: UUID, db: Session = Depends(get_db)):
    session_flow_service.get_session(db, session_id)
    return [batch_to_response(batch) for batch in session_flow_service.list_batches(db, session_id)]


@router.get("/{session_id}/current-batch", response_model=BatchResponse | None)
def current_batch(session_id: UUID, db: Session = Depends(get_db)):
    session_flow_service.get_session(db, session_id)
    return batch_to_response(session_flow_service.current_batch(db, session_id))


@router.get("/{session_id}/my-batch", response_model=MyBatchResponse)
def my_batch(session_id: UUID, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = student_service.get_by_user_id(db, current_user.user_id)
    return session_flow_service.build_my_batch(db, session_id, student.student_id)


@router.get("/{session_id}/monitor", response_model=SessionMonitorResponse)
def monitor_session(session_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    data = monitor_service.monitor(db, session_id)
    data["current_batch"] = batch_to_response(data["current_batch"])
    return data
