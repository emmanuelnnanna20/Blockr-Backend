from app.db.database import engine
from app.db.base import Base
from app.core.config import settings

def init_db():
    """Initialize database - create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()