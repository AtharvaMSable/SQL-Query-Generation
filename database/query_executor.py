"""
Query Executor Module
Safely executes validated SQL queries and returns results as DataFrames.
"""

from typing import Optional, Tuple
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
import logging

from config.database_config import DatabaseConfig
from config.settings import settings
from .validators import SQLValidator

logger = logging.getLogger(__name__)


class QueryExecutor:
    """
    Executes SQL queries safely after validation.
    Returns results as Pandas DataFrames for easy analysis and visualization.
    """
    
    def __init__(self):
        self.engine: Engine = DatabaseConfig.get_engine()
        self.validator = SQLValidator()
    
    def execute_query(
        self, 
        sql: str, 
        allowed_schema: str = None,
        add_limit: bool = True
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Execute SQL query with comprehensive safety checks.
        
        Args:
            sql: SQL query string
            allowed_schema: Schema to restrict query to
            add_limit: Whether to automatically add/enforce LIMIT clause
        
        Returns:
            Tuple of (DataFrame or None, error_message or None)
            On success: (DataFrame, None)
            On error: (None, error_message)
        """
        try:
            # 1. Sanitize the query
            sql = self.validator.sanitize_query(sql)
            logger.info(f"Executing query: {sql[:100]}...")
            
            # 2. Validate the query
            is_valid, error_msg = self.validator.validate_query(sql, allowed_schema)
            if not is_valid:
                logger.error(f"Query validation failed: {error_msg}")
                return None, f"Query validation failed: {error_msg}"
            
            # 3. Add/enforce LIMIT clause
            if add_limit:
                sql = self.validator.add_limit_clause(sql)
            
            # 4. Execute the query
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                
                # Convert to DataFrame
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                
                logger.info(
                    f"Query executed successfully. "
                    f"Rows returned: {len(df)}, Columns: {len(df.columns)}"
                )
                
                return df, None
                
        except Exception as e:
            error_msg = f"Query execution error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def execute_with_retry(
        self,
        sql: str,
        allowed_schema: str = None,
        max_retries: int = 2
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Execute query with automatic retry on transient failures.
        
        Args:
            sql: SQL query
            allowed_schema: Schema restriction
            max_retries: Maximum number of retry attempts
        
        Returns:
            Tuple of (DataFrame or None, error_message or None)
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            df, error = self.execute_query(sql, allowed_schema)
            
            if df is not None:
                if attempt > 0:
                    logger.info(f"Query succeeded on retry attempt {attempt}")
                return df, None
            
            last_error = error
            
            # Check if error is retryable (connection issues, timeouts, etc.)
            if attempt < max_retries:
                if self._is_retryable_error(error):
                    logger.warning(
                        f"Retryable error on attempt {attempt + 1}: {error}"
                    )
                    continue
                else:
                    # Non-retryable error, fail fast
                    break
        
        return None, last_error
    
    @staticmethod
    def _is_retryable_error(error: str) -> bool:
        """
        Determine if an error is transient and worth retrying.
        
        Args:
            error: Error message
        
        Returns:
            True if error is retryable
        """
        retryable_patterns = [
            'connection',
            'timeout',
            'deadlock',
            'temporary',
            'transient',
        ]
        
        error_lower = error.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)
    
    def get_query_explain(self, sql: str) -> Optional[str]:
        """
        Get query execution plan using EXPLAIN.
        Useful for query optimization and debugging.
        
        Args:
            sql: SQL query to explain
        
        Returns:
            EXPLAIN output as string, or None on error
        """
        try:
            explain_sql = f"EXPLAIN {sql}"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(explain_sql))
                explain_output = "\n".join([row[0] for row in result])
                
                return explain_output
                
        except Exception as e:
            logger.error(f"EXPLAIN error: {str(e)}")
            return None
    
    def validate_and_preview(
        self, 
        sql: str, 
        allowed_schema: str = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validate query and show what would be executed (without execution).
        
        Args:
            sql: SQL query
            allowed_schema: Schema restriction
        
        Returns:
            Tuple of (is_valid, message, modified_sql)
        """
        # Sanitize
        sql = self.validator.sanitize_query(sql)
        
        # Validate
        is_valid, error_msg = self.validator.validate_query(sql, allowed_schema)
        
        if not is_valid:
            return False, error_msg, None
        
        # Add limit for preview
        modified_sql = self.validator.add_limit_clause(sql)
        
        return True, "Query is valid", modified_sql
