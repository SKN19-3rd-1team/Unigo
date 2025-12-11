from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from backend.config import get_settings
import json

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
