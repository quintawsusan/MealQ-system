from app.repositories import meal_session_repository, serving_batch_repository
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError
from app.models.meal_session import MealSession
from app.models.serving_batch import ServingBatch
from app.models.student_meal_response import StudentMealResponse

def monitor(db: Session, session_id: int) -> dict:
    session = db.get(MealSession, session_id)
    if not session:
        raise NotFoundError('Meal session not found')
    current = serving_batch_repository.get_current(db, session_id)
    batch_counts = meal_session_repository.batch_counts(db, session_id)
    response_counts = meal_session_repository.get_response_counts(db, session_id)
    total_students = db.scalar(select(func.count(func.distinct(StudentMealResponse.student_id))).where(StudentMealResponse.session_id == session_id)) or 0
    return {'session': session, 'current_batch': current, 'total_students': total_students, 'going': response_counts.get('GOING', 0), 'skipped': response_counts.get('SKIPPED', 0), 'no_response': response_counts.get('NO_RESPONSE', 0), 'waiting_batches': batch_counts.get('WAITING', 0), 'called_batches': batch_counts.get('CALLED', 0), 'completed_batches': batch_counts.get('COMPLETED', 0)}
