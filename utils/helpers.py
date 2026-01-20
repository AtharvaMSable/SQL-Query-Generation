"""
Helper Utilities Module
Common utility functions used across the application.
"""

from datetime import datetime
from typing import Any
import re


def format_sql_for_display(sql: str) -> str:
    """
    Format SQL query for better readability in UI.
    
    Args:
        sql: Raw SQL query string
    
    Returns:
        Formatted SQL string
    """
    if not sql:
        return ""
    
    # Keywords to capitalize
    keywords = [
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
        'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'AS', 'ON',
        'AND', 'OR', 'IN', 'NOT', 'NULL', 'IS', 'LIKE', 'BETWEEN',
        'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT'
    ]
    
    formatted = sql
    
    # Add line breaks after major clauses
    formatted = re.sub(r'\s+(FROM|WHERE|GROUP BY|ORDER BY|HAVING|LIMIT)\s+', 
                       r'\n\1 ', formatted, flags=re.IGNORECASE)
    
    # Capitalize SQL keywords
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        formatted = re.sub(pattern, keyword.upper(), formatted, flags=re.IGNORECASE)
    
    # Clean up whitespace
    formatted = '\n'.join([line.strip() for line in formatted.split('\n')])
    
    return formatted


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object as string.
    
    Args:
        dt: Datetime object
        format: Format string
    
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    
    return dt.strftime(format)


def format_number(num: Any, decimals: int = 2) -> str:
    """
    Format number with thousand separators.
    
    Args:
        num: Number to format
        decimals: Number of decimal places
    
    Returns:
        Formatted number string
    """
    try:
        if isinstance(num, (int, float)):
            if isinstance(num, int):
                return f"{num:,}"
            else:
                return f"{num:,.{decimals}f}"
        return str(num)
    except:
        return str(num)


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary with default.
    
    Args:
        dictionary: Dictionary to query
        key: Key to retrieve
        default: Default value if key not found
    
    Returns:
        Value from dictionary or default
    """
    if dictionary is None:
        return default
    
    return dictionary.get(key, default)


def is_valid_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
    
    Returns:
        True if valid email format
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    return sanitized


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"
