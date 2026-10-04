import csv
import io
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status,UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin, require_student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate,StudentImportRow
from app.services import student_service

router=APIRouter(prefix="/students",tags=["Students"])
@router.get("/me",response_model=StudentResponse)
def get_my_student(current_user:
    User=Depends(require_student),db:Session=Depends(get_db)): 
    return student_service.get_by_user_id(db,current_user.user_id)

@router.get("",response_model=list[StudentResponse])
def list_students(offset:int=Query(0,ge=0),limit:int=Query(100,ge=1,le=500),_:
    User=Depends(require_admin),
    db:Session=Depends(get_db)): 
    return student_service.list_student(db,offset,limit)

@router.post("",response_model=StudentResponse,status_code=201)
def create_student(data:StudentCreate,current_user:
    User=Depends(require_admin),db:Session=Depends(get_db)):
    item=student_service.create_student(db,data); db.commit(); 
    return item

@router.post("/import")
async def import_students(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file",
        )

    contents = await file.read()

    try:
        text = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV file must use UTF-8 encoding",
        )

    reader = csv.DictReader(io.StringIO(text))

    required_columns = {
        "student_number",
        "first_name",
        "last_name",
        "class_name",
    }

    if not reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="CSV file is empty or has no header row",
        )

    missing_columns = required_columns - set(reader.fieldnames)

    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing CSV columns: {', '.join(sorted(missing_columns))}",
        )

    rows = []

    for row_number, row in enumerate(reader, start=2):
        try:
            rows.append(
                StudentImportRow(
                    student_number=int(row["student_number"]),
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    class_name=row["class_name"],
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data on CSV row {row_number}: {exc}",
            )

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="CSV file contains no student records",
        )

    result = student_service.bulk_import_students(db, rows)

    if result["total_errors"] > 0:
        raise HTTPException(
            status_code=400,
            detail=result,
        )

    return result

@router.get("/{student_id}",response_model=StudentResponse)
def get_student(student_id:UUID,current_user:
    User=Depends(require_admin),db:Session=Depends(get_db)): 
    return student_service.get_student(db,student_id)

@router.patch("/{student_id}",response_model=StudentResponse)
def update_student(student_id:UUID,data:StudentUpdate,current_user:
    User=Depends(require_admin),db:Session=Depends(get_db)):
    item=student_service.update_student(db,student_id,data); db.commit(); 
    return item

@router.delete("/{student_id}",status_code=204)
def delete_student(student_id:UUID,current_user:User=Depends(require_admin),db:Session=Depends(get_db)):
    student_service.delete_student(db,student_id); db.commit()
