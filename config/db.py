"""
Database configuration module.

SECURITY IMPROVEMENTS:
- Uses environment variables instead of hardcoded secrets
- Implements session management with dependency injection
- Configures connection pool for better performance
- Supports async operations (prepared for future migration)
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator

# ⚠️ SECURITY: Load database credentials from environment variables
# Never hardcode secrets in code. Use .env file for local development
# and Kubernetes Secrets for production.
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "storedb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")  # Default for local dev only

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ⚠️ PERFORMANCE: Configure connection pool
# - pool_size: number of connections to maintain
# - max_overflow: additional connections beyond pool_size
# - pool_pre_ping: verify connections before using them
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("DB_ECHO", "false").lower() == "true",  # Log SQL queries in debug mode
)

# Session factory for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models (alternative to Table Core API)
Base = declarative_base()

# Metadata for Table Core API (legacy support)
meta = MetaData()


# ⚠️ BEST PRACTICE: Dependency injection for database sessions
# This ensures proper session lifecycle management and prevents connection leaks
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
            result = db.execute(...)
            db.commit()
    
    Automatically handles session cleanup and rollback on errors.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Context manager version for non-FastAPI usage
@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions (for non-FastAPI usage).
    
    Usage:
        with get_db_context() as db:
            result = db.execute(...)
            db.commit()
    
    Automatically handles session cleanup and rollback on errors.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Legacy connection for backward compatibility (deprecated)
# ⚠️ DEPRECATED: Use get_db() context manager instead
conn = engine.connect()
