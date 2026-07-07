from app.core.config import settings
from app.core.logging import configure_logging
from app.core.errors import DomainError, domain_error_handler
configure_logging(settings.log_level)
try:
    from fastapi import FastAPI
    app = FastAPI(title='Digital Human Live API')
    app.add_exception_handler(DomainError, domain_error_handler)
    @app.get('/api/v1/healthz')
    def healthz(): return {'success': True, 'data': {'status': 'ok', 'env': settings.app_env}, 'error': None}
except ModuleNotFoundError:
    app = None
    def healthz(): return {'success': True, 'data': {'status': 'ok', 'env': settings.app_env}, 'error': None}
