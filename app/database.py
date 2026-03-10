from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Production-ready engine configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,          # number of persistent connections
    max_overflow=20,       # extra connections allowed temporarily
    pool_pre_ping=True,    # detects stale connections
    pool_recycle=1800,     # recycle connections every 30 min
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
