"""
Database Connection Module
Provides database connection management utilities.
"""

from sqlalchemy.engine import Connection, Engine
from contextlib import contextmanager
import logging

from config.database_config import DatabaseConfig

logger = logging.getLogger(__name__)


def get_database_connection() -> Engine:
    """
    Get the SQLAlchemy engine for database operations.
    
    Returns:
        SQLAlchemy Engine instance
    """
    return DatabaseConfig.get_engine()


@contextmanager
def get_connection():
    """
    Context manager for database connections.
    Automatically handles connection cleanup.
    
    Usage:
        with get_connection() as conn:
            result = conn.execute(query)
    
    Yields:
        SQLAlchemy Connection
    """
    engine = get_database_connection()
    conn = engine.connect()
    try:
        yield conn
    except Exception as e:
        logger.error(f"Database operation error: {str(e)}")
        raise
    finally:
        conn.close()


@contextmanager
def get_transaction():
    """
    Context manager for database transactions.
    Automatically commits on success or rolls back on error.
    
    Usage:
        with get_transaction() as conn:
            conn.execute(insert_query)
    
    Yields:
        SQLAlchemy Connection with active transaction
    """
    engine = get_database_connection()
    conn = engine.connect()
    trans = conn.begin()
    try:
        yield conn
        trans.commit()
    except Exception as e:
        trans.rollback()
        logger.error(f"Transaction error, rolled back: {str(e)}")
        raise
    finally:
        conn.close()
