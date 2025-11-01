from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import urllib.parse
import sys

# Validate DATABASE_URL exists
if not settings.DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set!", file=sys.stderr)
    sys.exit(1)

print(f"Connecting to database at: {settings.DATABASE_URL.split('@')[1].split('?')[0] if '@' in settings.DATABASE_URL else 'localhost'}", file=sys.stderr)

# Parse DATABASE_URL
parsed = urllib.parse.urlparse(settings.DATABASE_URL)

# Extract components with proper defaults
username = urllib.parse.unquote(parsed.username or "")
password = urllib.parse.unquote(parsed.password or "")
host = parsed.hostname
port = parsed.port

# Validate required components
if not host:
    print(f"ERROR: Could not parse hostname from DATABASE_URL: {settings.DATABASE_URL}", file=sys.stderr)
    sys.exit(1)

# Set default port if not provided
if port is None:
    port = 3306
    
database = parsed.path[1:] if parsed.path else ""

# Build clean URL WITHOUT any SSL params
clean_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

# SSL via connect_args (PyMySQL accepts this)
connect_args = {}
query_params = urllib.parse.parse_qs(parsed.query)

# Check for ssl-mode or ssl_mode in query parameters
if "ssl-mode" in query_params or "ssl_mode" in query_params or "ssl" in query_params:
    connect_args["ssl"] = {"ssl_mode": "REQUIRED"}
    print("SSL mode: REQUIRED", file=sys.stderr)

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