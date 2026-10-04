import asyncio
import contextlib
from app.routers import auth, device, health, meal_schedule, meal_session, meal_type, response, student
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.config import get_settings
from app.database import Base, SessionLocal, engine
from app.core.exceptions import AuthenticationError, BusinessRuleError, ConflictError, NotFoundError, ValidationError
from app.routers import user
from app.services import session_flow_service
from app.models.classroom import Classroom
from app.models.meal_type import MealType
from sqlalchemy import select
import app.models
from app.database import get_db
settings = get_settings()

Base.metadata.create_all(bind=engine)
with SessionLocal() as _db:
    for _name in ("Anita B", "Ada Lab", "Lovelace"):
        if not _db.scalar(select(Classroom).where(Classroom.name == _name)):
            _db.add(Classroom(name=_name))
    _db.commit()


async def flow_worker(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        print("[FLOW WORKER] tick", flush=True)
        db = SessionLocal()
        try:
            print("[FLOW WORKER] before worker_tick", flush=True)

            session_flow_service.worker_tick(db)

            print("[FLOW WORKER] after worker_tick", flush=True)

            db.commit()

            print("[FLOW WORKER] after commit", flush=True)

        except Exception as exc:
            db.rollback()
            print(
                f"[FLOW WORKER ERROR] {type(exc).__name__}: {exc}",
                flush=True,
            )
        finally:
            db.close()

        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=settings.flow_poll_interval_seconds,
            )
        except asyncio.TimeoutError:
            pass

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("[LIFESPAN] STARTING", flush=True)

    stop_event = asyncio.Event()
    task = asyncio.create_task(flow_worker(stop_event))

    print("[LIFESPAN] FLOW WORKER CREATED", flush=True)

    try:
        yield
    finally:
        print("[LIFESPAN] STOPPING", flush=True)
        stop_event.set()
        await task


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="MealQ cafeteria flow and student meals  API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(_: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(BusinessRuleError)
async def business_rule_handler(_: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
async def validation_error_handler(_: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(_: Request, exc: AuthenticationError):
    return JSONResponse(status_code=401, content={"detail": str(exc)}, headers={"WWW-Authenticate": "Bearer"})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "The operation conflicts with existing database data."})


app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(student.router, prefix="/api/v1")
app.include_router(device.router, prefix="/api/v1")
app.include_router(meal_type.router, prefix="/api/v1")
app.include_router(meal_schedule.router, prefix="/api/v1")
app.include_router(meal_session.router, prefix="/api/v1")
app.include_router(response.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "MealQ API works perfectly"}
