from fastapi import Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Raised for expected domain validation errors."""


async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": {"code": "DOMAIN_ERROR", "message": str(exc)},
        },
    )
