from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .context import get_context

# Get database URL from context
ctx = get_context()

# Create SQLAlchemy engine for SQLite
engine = create_engine(
    ctx.DB_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models (will be used in Hour 5)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()