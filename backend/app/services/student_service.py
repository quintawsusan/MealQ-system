from uuid import UUID
from typing import List
from sqlalchemy import select
import secrets
from app.core.security import hash_password
from sqlalchemy.orm import Session, joinedload
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models.student import Student
from app.models.user import User
from app.models.classroom import Classroom
from app.schemas.student import StudentCreate, StudentUpdate, StudentImportRow

ALLOWED_CLASSES={"Anita B","Ada Lab","Lovelace"}
def get_by_id(db,student_id:UUID):
    student=db.query(Student).options(joinedload(Student.classroom)).filter(Student.student_id==student_id).first()
    if not student: raise NotFoundError("Student not found")
    return student

def get_by_user_id(db,user_id:UUID):
    student=db.query(Student).options(joinedload(Student.classroom)).filter(Student.user_id==user_id).first()
    if not student: raise NotFoundError("Student profile not found")
    return student

def list(db,offset,limit): 
    return db.query(Student).options(joinedload(Student.classroom)).join(User).filter(User.is_active.is_(True),User.role=="STUDENT").offset(offset).limit(limit).all()

def create(db,data):
    user=db.get(User,data.user_id)
    if not user: raise NotFoundError("User not found")
    if user.role!="STUDENT": raise BusinessRuleError("Only STUDENT users can have a student profile")
    if db.query(Student).filter_by(user_id=data.user_id).first(): raise ConflictError("User already has a student profile")
    if db.query(Student).filter_by(student_number=data.student_number).first(): raise ConflictError("Student number is already in use")
    classroom=db.query(Classroom).filter_by(name=data.class_name).first()
    if not classroom: raise BusinessRuleError("class must be one of: Anita B, Ada Lab, Lovelace")
    item=Student(user_id=data.user_id,student_number=data.student_number,class_id=classroom.id); db.add(item); db.flush(); return item

def bulk_import(db: Session, rows: List[StudentImportRow]):
    created = []
    errors = []

    seen_student_numbers = set()

    for row_number, row in enumerate(rows, start=2):
        try:
            # Check duplicate student number inside the CSV
            if row.student_number in seen_student_numbers:
                raise ConflictError(
                    f"Student number {row.student_number} appears more than once in the file"
                )

            seen_student_numbers.add(row.student_number)

            # Check whether student already exists
            existing_student = db.scalar(
                select(Student).where(
                    Student.student_number == row.student_number
                )
            )

            if existing_student:
                raise ConflictError(
                    f"Student number {row.student_number} is already registered"
                )

            # Check classroom
            classroom = db.scalar(
                select(Classroom).where(
                    Classroom.name == row.class_name.strip()
                )
            )

            if not classroom:
                raise BusinessRuleError(
                    f"Class '{row.class_name}' does not exist"
                )

            # Generate login credentials
            username = f"student{row.student_number}"
            temporary_password = secrets.token_urlsafe(8)

            # Make sure generated username is not already used
            existing_user = db.scalar(
                select(User).where(User.user_name == username)
            )

            if existing_user:
                raise ConflictError(
                    f"Username '{username}' is already in use"
                )

            # We need a unique email because User.email is NOT NULL and UNIQUE.
            email = f"student{row.student_number}@mealq.local"

            existing_email = db.scalar(
                select(User).where(User.email == email)
            )

            if existing_email:
                raise ConflictError(
                    f"Email '{email}' is already in use"
                )

            # Create User
            user = User(
                first_name=row.first_name.strip(),
                last_name=row.last_name.strip(),
                user_name=username,
                email=email,
                password_hash=hash_password(temporary_password),
                role="STUDENT",
                is_active=True,
                email_verified=True,
            )

            db.add(user)
            db.flush()

            # Create Student profile
            student = Student(
                user_id=user.user_id,
                student_number=row.student_number,
                class_id=classroom.id,
            )

            db.add(student)
            db.flush()

            created.append(
                {
                    "student_number": row.student_number,
                    "name": f"{row.first_name.strip()} {row.last_name.strip()}",
                    "username": username,
                    "temporary_password": temporary_password,
                    "class_name": classroom.name,
                }
            )

        except Exception as exc:
            errors.append(
                {
                    "row": row_number,
                    "student_number": row.student_number,
                    "error": str(exc),
                }
            )

    # If anything failed, roll back the entire import.
    if errors:
        db.rollback()
        return {
            "created": [],
            "errors": errors,
            "total_created": 0,
            "total_errors": len(errors),
        }

    db.commit()

    return {
        "created": created,
        "errors": [],
        "total_created": len(created),
        "total_errors": 0,
    }
    
def update(db,student_id,data):
    student=get_by_id(db,student_id); values=data.model_dump(exclude_unset=True)
    if "class_name" in values:
        classroom=db.query(Classroom).filter_by(name=values.pop("class_name")).first()
        if not classroom: raise BusinessRuleError("class must be one of: Anita B, Ada Lab, Lovelace")
        student.class_id=classroom.id
    db.flush(); return student
    
def delete(db,student_id):
    student=get_by_id(db,student_id)
    if student.meal_responses or student.batch_memberships: raise BusinessRuleError("Cannot delete a student with existing meal session history")
    db.delete(student); db.flush()
get_student=get_by_id; list_student=list; create_student=create; update_student=update; delete_student=delete

bulk_import_students = bulk_import
