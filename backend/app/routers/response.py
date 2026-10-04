from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin, require_student
from app.models.user import User
from app.repositories import student_meal_response_repository
from app.schemas.response import StudentMealResponseCreate, StudentMealResponseResponse
from app.services import session_flow_service
from app.services import student_service

router = APIRouter(prefix="/meal-sessions", tags=["Student Responses"])


@router.post("/{session_id}/responses/me", response_model=StudentMealResponseResponse)
def submit_my_response(
    session_id: UUID,
    data: StudentMealResponseCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    student = student_service.get_by_user_id(db, current_user.user_id)
    item = session_flow_service.respond(db, session_id, student.student_id, data.response.value)
    db.commit()
    return item


@router.get("/{session_id}/responses", response_model=list[StudentMealResponseResponse])
def list_responses(session_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    session_flow_service.get_session(db, session_id)
    return student_meal_response_repository.list_for_session(db, session_id)
