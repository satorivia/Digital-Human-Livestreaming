from fastapi import FastAPI

from app.core.config import settings
from app.core.errors import DomainError, domain_error_handler
from app.core.logging import configure_logging
from app.api.routes import router as api_router

configure_logging(settings.log_level)

app = FastAPI(title="Digital Human Live API")
app.add_exception_handler(DomainError, domain_error_handler)
app.include_router(api_router)


@app.get("/api/v1/healthz")
def healthz() -> dict[str, object]:
    return {"success": True, "data": {"status": "ok", "env": settings.app_env}, "error": None}
