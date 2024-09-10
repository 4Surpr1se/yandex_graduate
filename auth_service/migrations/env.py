import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# Импорт вашего конфигурационного файла
from src.core.config import settings
# Импорт базы данных для метаданных
from src.db.postgres import Base
from src.models.role import Role
# Импорт моделей
from src.models.user import User
from src.models.user_roles import UserRole

# Включение конфигурации логирования из alembic.ini
config = context.config
fileConfig(config.config_file_name)
env_path = config.get_main_option("env_file")

if env_path:
    load_dotenv(os.path.join(os.path.dirname(__file__), env_path))

config.set_main_option(
    'sqlalchemy.url',
    f'postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}'
)

# Указываем Alembic, где искать метаданные для создания миграций
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций в режиме "offline"."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запуск миграций в режиме "online"."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
