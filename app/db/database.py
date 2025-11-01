from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import urllib.parse
import sys

# Validate DATABASE_URL exists
if not settings.DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set!", file=sys.stderr)
    sys.exit(1)

print(f"Attempting to connect to database...", file=sys.stderr)

# Parse DATABASE_URL
parsed = urllib.parse.urlparse(settings.DATABASE_URL)

# Extract components
username = urllib.parse.unquote(parsed.username or "")
password = urllib.parse.unquote(parsed.password or "")
host = parsed.hostname
port = parsed.port

# Validate required components
if not host:
    print(f"ERROR: Could not parse hostname from DATABASE_URL", file=sys.stderr)
    sys.exit(1)

# Set default port if not provided
if port is None:
    port = 3306
    
database = parsed.path[1:] if parsed.path else ""

print(f"Database host: {host}:{port}", file=sys.stderr)
print(f"Database name: {database}", file=sys.stderr)

# Build clean URL WITHOUT any SSL params in the URL
clean_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

# Configure SSL via connect_args for Aiven
connect_args = {}
query_params = urllib.parse.parse_qs(parsed.query)

# Aiven requires SSL - configure it properly for PyMySQL
if "ssl-mode" in query_params or "ssl_mode" in query_params or "ssl" in query_params:
    # PyMySQL SSL configuration for Aiven
    connect_args["ssl"] = {
        "ssl_mode": "REQUIRED"
    }
    print("SSL mode: REQUIRED (Aiven Cloud)", file=sys.stderr)
else:
    # Force SSL even if not in URL (Aiven requires it)
    connect_args["ssl"] = {
        "ssl_mode": "REQUIRED"
    }
    print("SSL mode: REQUIRED (forced for cloud database)", file=sys.stderr)

# Create engine with appropriate settings for cloud database
engine = create_engine(
    clean_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Smaller pool for free tier
    max_overflow=10,  # Allow up to 15 total connections
    pool_recycle=3600,  # Recycle connections after 1 hour
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

# Test connection on startup
try:
    with engine.connect() as conn:
        print("✓ Database connection successful!", file=sys.stderr)
except Exception as e:
    print(f"✗ Database connection failed: {e}", file=sys.stderr)
    # Don't exit - let the app start and fail on first request with better error