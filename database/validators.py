"""
SQL Validator Module
Validates SQL queries for safety and compliance with security rules.
"""

import re
from typing import Tuple, List
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class SQLValidator:
    """
    Validates SQL queries to ensure they are safe for execution.
    Implements multiple layers of security checks.
    """
    
    @staticmethod
    def validate_query(sql: str, allowed_schema: str = None) -> Tuple[bool, str]:
        """
        Comprehensive SQL validation.
        
        Args:
            sql: SQL query string to validate
            allowed_schema: Schema name that queries must be restricted to
        
        Returns:
            Tuple of (is_valid: bool, error_message: str)
            If valid, error_message is empty string
        """
        # Strip whitespace and normalize
        sql = sql.strip()
        sql_upper = sql.upper()
        
        # 1. Check if query is empty
        if not sql:
            return False, "Empty query"
        
        # 2. Check for forbidden keywords (DML/DDL)
        forbidden_found = SQLValidator._check_forbidden_keywords(sql_upper)
        if forbidden_found:
            logger.warning(f"Forbidden keyword detected: {forbidden_found}")
            return False, f"Forbidden operation detected: {forbidden_found}"
        
        # 3. Ensure query is a SELECT statement
        if not sql_upper.strip().startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # 4. Check for multiple statements (SQL injection attempt)
        if ';' in sql[:-1]:  # Allow trailing semicolon
            return False, "Multiple statements not allowed"
        
        # 5. Check for comments (potential obfuscation)
        if '--' in sql or '/*' in sql or '*/' in sql:
            return False, "SQL comments not allowed"
        
        # 6. Validate schema restriction if provided
        if allowed_schema:
            is_valid, msg = SQLValidator._validate_schema_restriction(sql, allowed_schema)
            if not is_valid:
                return False, msg
        
        # 7. Ensure LIMIT clause exists
        if 'LIMIT' not in sql_upper:
            logger.info("Query missing LIMIT clause, will be added automatically")
        
        # 8. Check for suspicious patterns
        suspicious = SQLValidator._check_suspicious_patterns(sql)
        if suspicious:
            return False, f"Suspicious pattern detected: {suspicious}"
        
        return True, ""
    
    @staticmethod
    def _check_forbidden_keywords(sql_upper: str) -> str:
        """
        Check for forbidden SQL keywords.
        
        Returns:
            Empty string if OK, otherwise the forbidden keyword found
        """
        for keyword in settings.FORBIDDEN_SQL_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                return keyword
        return ""
    
    @staticmethod
    def _validate_schema_restriction(sql: str, allowed_schema: str) -> Tuple[bool, str]:
        """
        Ensure query only references tables from the allowed schema.
        
        Args:
            sql: SQL query
            allowed_schema: Schema name to restrict to
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Extract table references using regex
        # Matches: schema.table or just table
        pattern = r'(?:FROM|JOIN)\s+(?:(\w+)\.)?(\w+)'
        matches = re.findall(pattern, sql, re.IGNORECASE)
        
        for schema, table in matches:
            if schema and schema.lower() != allowed_schema.lower():
                return False, f"Access denied to schema: {schema}"
        
        return True, ""
    
    @staticmethod
    def _check_suspicious_patterns(sql: str) -> str:
        """
        Check for suspicious SQL patterns that might indicate injection attempts.
        
        Returns:
            Empty string if OK, otherwise description of suspicious pattern
        """
        suspicious_patterns = [
            (r'\bOR\s+1\s*=\s*1\b', "SQL injection pattern (OR 1=1)"),
            (r'\bUNION\s+SELECT\b', "UNION-based injection attempt"),
            (r';\s*DROP\b', "DROP statement injection"),
            (r';\s*DELETE\b', "DELETE statement injection"),
            (r'\bINTO\s+OUTFILE\b', "File write attempt"),
            (r'\bLOAD_FILE\b', "File read attempt"),
            (r'\bEXEC\b', "EXEC command"),
            (r'\bEXECUTE\b', "EXECUTE command"),
            (r'xp_cmdshell', "Command shell access attempt"),
        ]
        
        sql_upper = sql.upper()
        
        for pattern, description in suspicious_patterns:
            if re.search(pattern, sql_upper):
                logger.warning(f"Suspicious pattern detected: {description}")
                return description
        
        return ""
    
    @staticmethod
    def add_limit_clause(sql: str, max_limit: int = None) -> str:
        """
        Add or enforce LIMIT clause to SQL query.
        
        Args:
            sql: SQL query
            max_limit: Maximum number of rows (defaults to settings.MAX_QUERY_ROWS)
        
        Returns:
            SQL query with LIMIT clause
        """
        if max_limit is None:
            max_limit = settings.MAX_QUERY_ROWS
        
        sql = sql.strip()
        sql_upper = sql.upper()
        
        # If LIMIT already exists, validate it's not too high
        if 'LIMIT' in sql_upper:
            # Extract existing limit value
            match = re.search(r'LIMIT\s+(\d+)', sql_upper)
            if match:
                existing_limit = int(match.group(1))
                if existing_limit > max_limit:
                    # Replace with max allowed
                    sql = re.sub(
                        r'LIMIT\s+\d+', 
                        f'LIMIT {max_limit}', 
                        sql, 
                        flags=re.IGNORECASE
                    )
                    logger.info(f"Reduced LIMIT from {existing_limit} to {max_limit}")
        else:
            # Add LIMIT clause
            # Remove trailing semicolon if present
            if sql.endswith(';'):
                sql = sql[:-1]
            sql = f"{sql} LIMIT {max_limit}"
            logger.debug(f"Added LIMIT {max_limit} to query")
        
        return sql
    
    @staticmethod
    def sanitize_query(sql: str) -> str:
        """
        Sanitize SQL query by removing dangerous elements.
        
        Args:
            sql: Raw SQL query
        
        Returns:
            Sanitized SQL query
        """
        # Remove SQL comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Remove multiple semicolons
        sql = re.sub(r';+', ';', sql)
        
        # Normalize whitespace
        sql = ' '.join(sql.split())
        
        return sql.strip()
    
    @staticmethod
    def extract_tables_from_query(sql: str) -> List[str]:
        """
        Extract table names referenced in the SQL query.
        
        Args:
            sql: SQL query
        
        Returns:
            List of table names
        """
        # Pattern to match FROM and JOIN clauses
        pattern = r'(?:FROM|JOIN)\s+(?:\w+\.)?(\w+)'
        matches = re.findall(pattern, sql, re.IGNORECASE)
        
        # Remove duplicates and return
        return list(set(matches))
