from app.db.database import engine
from app.db.base import Base

# Create tables
Base.metadata.create_all(bind=engine)
print("✅ Database ready!")