from alembic import context
from sqlalchemy import MetaData
config=context.config
target_metadata=MetaData()
def run_migrations_offline(): context.configure(url=config.get_main_option('sqlalchemy.url'), target_metadata=target_metadata); context.run_migrations()
def run_migrations_online():
    from sqlalchemy import create_engine
    with create_engine(config.get_main_option('sqlalchemy.url')).connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata); context.run_migrations()
run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
