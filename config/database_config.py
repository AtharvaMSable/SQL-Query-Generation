"""
Database Configuration for Neon PostgreSQL
Manages SQLAlchemy engine creation and connection pooling.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from typing import Optional
import logging

from .settings import settings

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Database configuration and engine management.
    Implements singleton pattern for connection pooling efficiency.
    """
    
    _engine: Optional[Engine] = None
    
    @classmethod
    def get_engine(cls, echo: bool = False) -> Engine:
        """
        Get or create SQLAlchemy engine with connection pooling.
        
        Args:
            echo: If True, log all SQL statements (useful for debugging)
        
        Returns:
            SQLAlchemy Engine instance
        
        Connection pool settings:
        - pool_size: Number of connections to maintain
        - max_overflow: Additional connections allowed beyond pool_size
        - pool_timeout: Seconds to wait for connection from pool
        - pool_recycle: Recycle connections after N seconds (prevents stale connections)
        """
        if cls._engine is None:
            try:
                database_url = settings.get_database_url()
                
                # Create engine with connection pooling for production use
                cls._engine = create_engine(
                    database_url,
                    poolclass=QueuePool,
                    pool_size=5,           # Base pool size
                    max_overflow=10,       # Allow up to 15 total connections
                    pool_timeout=30,       # Wait 30s for available connection
                    pool_recycle=3600,     # Recycle connections every hour
                    pool_pre_ping=True,    # Verify connections before using
                    echo=echo,             # Log SQL (False in production)
                )
                
                logger.info(
                    f"Database engine created successfully. "
                    f"Connected to Neon PostgreSQL"
                )
                
            except Exception as e:
                logger.error(f"Failed to create database engine: {str(e)}")
                raise
        
        return cls._engine
    
    @classmethod
    def test_connection(cls) -> bool:
        """
        Test database connectivity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            engine = cls.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    @classmethod
    def close_engine(cls):
        """
        Dispose of the engine and close all connections.
        Should be called on application shutdown.
        """
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None
            logger.info("Database engine disposed")
    
    @classmethod
    def get_connection_info(cls) -> dict:
        """
        Get database connection information (for debugging/monitoring).
        Sensitive information is masked.
        """
        return {
            'host': settings.NEON_DB_HOST,
            'database': settings.NEON_DB_NAME,
            'user': settings.NEON_DB_USER,
            'port': settings.NEON_DB_PORT,
            'environment': settings.APP_ENV,
        }
