class DomainError(Exception): pass
async def domain_error_handler(_, exc: DomainError):
    return {'success': False, 'data': None, 'error': {'code': 'DOMAIN_ERROR', 'message': str(exc)}}
