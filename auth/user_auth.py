"""User authentication and database login"""

import hashlib
import logging
from typing import Optional, Dict, List
from sqlalchemy import text
from sqlalchemy.engine import Engine

from config.database_config import DatabaseConfig

logger = logging.getLogger(__name__)


class UserAuth:
    """
    User authentication and authorization manager.
    Validates credentials and retrieves user permissions.
    """
    
    def __init__(self):
        self.engine: Engine = DatabaseConfig.get_engine()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using SHA-256.
        In production, use bcrypt or argon2 for stronger security.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user credentials against the database.
        
        Args:
            username: User's username/email
            password: User's password (plain text)
        
        Returns:
            User info dict if authenticated, None otherwise
            Dict contains: user_id, username, email, full_name, role
        """
        try:
            hashed_password = self._hash_password(password)
            
            query = text("""
                SELECT 
                    user_id,
                    username,
                    email,
                    full_name,
                    role,
                    is_active
                FROM users
                WHERE username = :username 
                  AND password_hash = :password_hash
                  AND is_active = TRUE
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    query, 
                    {"username": username, "password_hash": hashed_password}
                )
                row = result.fetchone()
                
                if row:
                    user_info = {
                        'user_id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'full_name': row[3],
                        'role': row[4],
                        'is_active': row[5],
                    }
                    logger.info(f"User authenticated successfully: {username}")
                    return user_info
                else:
                    logger.warning(f"Authentication failed for user: {username}")
                    return None
                    
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    def get_user_datasets(self, user_id: int) -> List[Dict]:
        """
        Get all datasets accessible by the user.
        
        Args:
            user_id: User's ID
        
        Returns:
            List of dataset dictionaries with dataset_id, name, description, schema_name
        """
        try:
            query = text("""
                SELECT 
                    d.dataset_id,
                    d.dataset_name,
                    d.description,
                    d.schema_name,
                    d.created_at,
                    uda.access_level
                FROM datasets d
                INNER JOIN user_dataset_access uda 
                    ON d.dataset_id = uda.dataset_id
                WHERE uda.user_id = :user_id
                  AND uda.is_active = TRUE
                  AND d.is_active = TRUE
                ORDER BY d.dataset_name
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                datasets = []
                
                for row in result:
                    datasets.append({
                        'dataset_id': row[0],
                        'dataset_name': row[1],
                        'description': row[2],
                        'schema_name': row[3],
                        'created_at': row[4],
                        'access_level': row[5],
                    })
                
                logger.info(f"Retrieved {len(datasets)} datasets for user_id: {user_id}")
                return datasets
                
        except Exception as e:
            logger.error(f"Error retrieving user datasets: {str(e)}")
            return []
    
    def verify_dataset_access(self, user_id: int, dataset_id: int) -> bool:
        """
        Verify if user has access to a specific dataset.
        
        Args:
            user_id: User's ID
            dataset_id: Dataset ID to check
        
        Returns:
            True if user has access, False otherwise
        """
        try:
            query = text("""
                SELECT COUNT(*) 
                FROM user_dataset_access
                WHERE user_id = :user_id 
                  AND dataset_id = :dataset_id
                  AND is_active = TRUE
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    query, 
                    {"user_id": user_id, "dataset_id": dataset_id}
                )
                count = result.scalar()
                
                has_access = count > 0
                logger.debug(
                    f"Dataset access check: user_id={user_id}, "
                    f"dataset_id={dataset_id}, has_access={has_access}"
                )
                return has_access
                
        except Exception as e:
            logger.error(f"Error verifying dataset access: {str(e)}")
            return False
    
    def get_dataset_info(self, dataset_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific dataset.
        
        Args:
            dataset_id: Dataset ID
        
        Returns:
            Dataset info dict or None if not found
        """
        try:
            query = text("""
                SELECT 
                    dataset_id,
                    dataset_name,
                    description,
                    schema_name,
                    created_at,
                    is_active
                FROM datasets
                WHERE dataset_id = :dataset_id
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"dataset_id": dataset_id})
                row = result.fetchone()
                
                if row:
                    return {
                        'dataset_id': row[0],
                        'dataset_name': row[1],
                        'description': row[2],
                        'schema_name': row[3],
                        'created_at': row[4],
                        'is_active': row[5],
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving dataset info: {str(e)}")
            return None
    
    def log_query_history(
        self, 
        user_id: int, 
        dataset_id: int, 
        question: str, 
        generated_sql: str,
        row_count: int
    ) -> bool:
        """
        Log user query to history table for audit and analytics.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
            question: Natural language question
            generated_sql: Generated SQL query
            row_count: Number of rows returned
        
        Returns:
            True if logged successfully
        """
        try:
            query = text("""
                INSERT INTO query_history 
                    (user_id, dataset_id, question, generated_sql, row_count, created_at)
                VALUES 
                    (:user_id, :dataset_id, :question, :generated_sql, :row_count, NOW())
            """)
            
            with self.engine.begin() as conn:  # Use transaction
                conn.execute(
                    query,
                    {
                        "user_id": user_id,
                        "dataset_id": dataset_id,
                        "question": question,
                        "generated_sql": generated_sql,
                        "row_count": row_count,
                    }
                )
                logger.debug(f"Query logged for user_id: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error logging query history: {str(e)}")
            return False
