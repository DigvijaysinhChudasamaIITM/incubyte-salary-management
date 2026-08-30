from fastapi import FastAPI

from salary_management.api.employees import router as employee_router


def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> FastAPI:
    application = FastAPI(title="Salary Management API", version="0.1.0")
    application.include_router(employee_router)
    application.add_api_route("/health", health, methods=["GET"], tags=["system"])
    return application


app = create_app()
