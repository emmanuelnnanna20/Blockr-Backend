from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import urllib.parse

# Parse DATABASE_URL
parsed = urllib.parse.urlparse(settings.DATABASE_URL)

# Extract components
username = urllib.parse.unquote(parsed.username or "")
password = urllib.parse.unquote(parsed.password or "")
host = parsed.hostname
port = parsed.port
database = parsed.path[1:]  # remove leading '/'

# Build clean URL WITHOUT any SSL params
clean_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

# SSL via connect_args (PyMySQL accepts this)
connect_args = {}
if "ssl" in parsed.query or "ssl_mode" in parsed.query:
    connect_args["ssl_mode"] = "REQUIRED"  # or "PREFERRED"

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