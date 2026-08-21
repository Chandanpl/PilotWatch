from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.config import settings

# Configure SQLite database engine with thread isolation disabled for dev server
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency to inject database sessions securely and clean them up on complete."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
