from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import settings and database
from app.core.config import settings

# Import Base and ALL models - this is critical for autogenerate
from app.db.base import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    import urllib.parse
    
    # Parse the DATABASE_URL to add PyMySQL driver
    parsed = urllib.parse.urlparse(settings.DATABASE_URL)
    
    # Extract components
    username = urllib.parse.unquote(parsed.username or "")
    password = urllib.parse.unquote(parsed.password or "")
    host = parsed.hostname
    port = parsed.port if parsed.port else 3306
    database = parsed.path[1:] if parsed.path else ""
    
    # Build URL with PyMySQL driver
    database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    
    # Create engine configuration
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = database_url
    
    # Add pymysql-specific configuration with SSL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={
            "ssl": {"ssl_mode": "REQUIRED"},
            "charset": "utf8mb4"
        }
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()