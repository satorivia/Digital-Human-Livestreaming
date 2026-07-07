from dataclasses import dataclass
@dataclass
class ApiResponse:
    success: bool = True
    data: object | None = None
    error: dict[str, str] | None = None
