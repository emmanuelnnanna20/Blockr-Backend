from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import urllib.parse

# Parse DATABASE_URL
parsed = urllib.parse.urlparse(settings.DATABASE_URL)

# Extract components with proper defaults
username = urllib.parse.unquote(parsed.username or "")
password = urllib.parse.unquote(parsed.password or "")
host = parsed.hostname or "localhost"
port = parsed.port if parsed.port is not None else 3306  # Default MySQL port
database = parsed.path[1:] if parsed.path else ""  # remove leading '/'

# Build clean URL WITHOUT any SSL params
clean_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

# SSL via connect_args (PyMySQL accepts this)
connect_args = {}
query_params = urllib.parse.parse_qs(parsed.query)

# Check for ssl-mode or ssl_mode in query parameters
if "ssl-mode" in query_params or "ssl_mode" in query_params:
    connect_args["ssl"] = {"ssl_mode": "REQUIRED"}
elif "ssl" in query_params:
    connect_args["ssl"] = {"ssl_mode": "REQUIRED"}

# Create engine
engine = create_engine(
    clean_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()