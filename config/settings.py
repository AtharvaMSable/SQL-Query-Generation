"""
Application Settings and Configuration
Loads environment variables and provides application-wide constants.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Centralized application settings.
    All configuration is loaded from environment variables for 12-factor app compliance.
    """
    
    # Application Settings
    APP_NAME: str = os.getenv('APP_NAME', 'AskQL Analytics Platform')
    APP_ENV: str = os.getenv('APP_ENV', 'development')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Neon PostgreSQL Database Configuration
    NEON_DB_URL: str = os.getenv('NEON_DB_URL', '')
    
    # Google Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # Security Settings
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv('SESSION_TIMEOUT_MINUTES', '60'))
    MAX_QUERY_ROWS: int = int(os.getenv('MAX_QUERY_ROWS', '10000'))
    
    # Query Validation Rules
    ALLOWED_SQL_KEYWORDS: list = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 
                                   'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'AS',
                                   'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AND', 
                                   'OR', 'IN', 'NOT', 'LIKE', 'BETWEEN', 'IS', 'NULL',
                                   'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT']
    
    FORBIDDEN_SQL_KEYWORDS: list = ['DELETE', 'UPDATE', 'INSERT', 'DROP', 
                                     'ALTER', 'TRUNCATE', 'CREATE', 'GRANT',
                                     'REVOKE', 'EXEC', 'EXECUTE', 'CALL']
    
    # Streamlit UI Configuration
    PAGE_TITLE: str = "AskQL - AI Analytics"
    PAGE_ICON: str = "🤖"
    LAYOUT: str = "wide"
    
    # LLM Configuration
    LLM_TEMPERATURE: float = 0.1  # Low temperature for deterministic SQL generation
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT_SECONDS: int = 30
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.
        Returns True if valid, raises ValueError if missing critical config.
        """
        required_vars = [
            ('NEON_DB_URL', cls.NEON_DB_URL),
            ('GEMINI_API_KEY', cls.GEMINI_API_KEY),
        ]
        
        missing = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please check your .env file."
            )
        
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Get PostgreSQL connection URL for SQLAlchemy.
        Returns the configured NEON_DB_URL.
        """
        return cls.NEON_DB_URL
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.APP_ENV.lower() == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.APP_ENV.lower() == 'development'


# Create a singleton instance
settings = Settings()
