import os
class Settings:
    app_env=os.getenv('APP_ENV','local')
    database_url=os.getenv('DATABASE_URL','sqlite+aiosqlite:///./dev.db')
    redis_url=os.getenv('REDIS_URL','redis://localhost:6379/0')
    qdrant_url=os.getenv('QDRANT_URL','http://localhost:6333')
    minio_endpoint=os.getenv('MINIO_ENDPOINT','http://localhost:9000')
    srs_webrtc_base_url=os.getenv('SRS_WEBRTC_BASE_URL','http://localhost:8080')
    log_level=os.getenv('LOG_LEVEL','INFO')
settings=Settings()
