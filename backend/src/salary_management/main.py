from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from salary_management.api.employees import router as employee_router
from salary_management.config import cors_allowed_origins
from salary_management.persistence.database import get_session


def health() -> dict[str, str]:
    return {"status": "ok"}


def readiness(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database is unavailable") from None
    return {"status": "ready"}


def create_app() -> FastAPI:
    application = FastAPI(title="Salary Management API", version="0.1.0")
    allowed_origins = cors_allowed_origins()
    if allowed_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=False,
            allow_methods=["GET"],
            allow_headers=["Accept", "Content-Type"],
        )
    application.include_router(employee_router)
    application.add_api_route("/health", health, methods=["GET"], tags=["system"])
    application.add_api_route("/ready", readiness, methods=["GET"], tags=["system"])
    return application


app = create_app()
