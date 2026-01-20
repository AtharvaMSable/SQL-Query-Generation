"""
Schema Loader Module
Dynamically loads and introspects database schemas for authorized datasets.
"""

from typing import List, Dict, Optional
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
import logging

from config.database_config import DatabaseConfig

logger = logging.getLogger(__name__)


class SchemaLoader:
    """
    Loads and provides database schema metadata.
    Used for generating schema-aware prompts for the LLM.
    """
    
    def __init__(self):
        self.engine: Engine = DatabaseConfig.get_engine()
    
    def get_schema_tables(self, schema_name: str) -> List[str]:
        """
        Get all tables in a specific schema.
        
        Args:
            schema_name: PostgreSQL schema name
        
        Returns:
            List of table names
        """
        try:
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = :schema_name
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"schema_name": schema_name})
                tables = [row[0] for row in result]
                logger.info(f"Found {len(tables)} tables in schema: {schema_name}")
                return tables
                
        except Exception as e:
            logger.error(f"Error loading tables for schema {schema_name}: {str(e)}")
            return []
    
    def get_table_columns(self, schema_name: str, table_name: str) -> List[Dict]:
        """
        Get columns and metadata for a specific table.
        
        Args:
            schema_name: PostgreSQL schema name
            table_name: Table name
        
        Returns:
            List of dictionaries containing column metadata:
            - column_name: Name of the column
            - data_type: PostgreSQL data type
            - is_nullable: Whether column allows NULL
            - column_default: Default value if any
        """
        try:
            query = text("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = :schema_name
                  AND table_name = :table_name
                ORDER BY ordinal_position
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    query, 
                    {"schema_name": schema_name, "table_name": table_name}
                )
                
                columns = []
                for row in result:
                    columns.append({
                        'column_name': row[0],
                        'data_type': row[1],
                        'is_nullable': row[2] == 'YES',
                        'column_default': row[3],
                        'max_length': row[4],
                    })
                
                logger.debug(
                    f"Loaded {len(columns)} columns for "
                    f"{schema_name}.{table_name}"
                )
                return columns
                
        except Exception as e:
            logger.error(
                f"Error loading columns for {schema_name}.{table_name}: {str(e)}"
            )
            return []
    
    def get_full_schema_metadata(self, schema_name: str) -> Dict:
        """
        Get complete schema metadata including all tables and columns.
        This is used to generate the context for LLM prompts.
        
        Args:
            schema_name: PostgreSQL schema name
        
        Returns:
            Dictionary with schema metadata:
            {
                'schema_name': str,
                'tables': [
                    {
                        'table_name': str,
                        'columns': [
                            {
                                'column_name': str,
                                'data_type': str,
                                'is_nullable': bool
                            }
                        ]
                    }
                ]
            }
        """
        try:
            tables = self.get_schema_tables(schema_name)
            
            schema_metadata = {
                'schema_name': schema_name,
                'tables': []
            }
            
            for table_name in tables:
                columns = self.get_table_columns(schema_name, table_name)
                
                schema_metadata['tables'].append({
                    'table_name': table_name,
                    'row_count': self._get_table_row_count(schema_name, table_name),
                    'columns': columns
                })
            
            logger.info(
                f"Loaded full schema metadata for: {schema_name} "
                f"({len(tables)} tables)"
            )
            return schema_metadata
            
        except Exception as e:
            logger.error(f"Error loading full schema metadata: {str(e)}")
            return {'schema_name': schema_name, 'tables': []}
    
    def _get_table_row_count(self, schema_name: str, table_name: str) -> int:
        """
        Get approximate row count for a table.
        Uses pg_class for performance (exact count can be slow on large tables).
        
        Args:
            schema_name: Schema name
            table_name: Table name
        
        Returns:
            Approximate row count
        """
        try:
            query = text(f"""
                SELECT reltuples::BIGINT AS estimate
                FROM pg_class
                WHERE relname = :table_name
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"table_name": table_name})
                row = result.fetchone()
                return int(row[0]) if row else 0
                
        except Exception:
            # If estimation fails, return 0
            return 0
    
    def format_schema_for_llm(self, schema_name: str) -> str:
        """
        Format schema metadata as a string for LLM prompt injection.
        Creates a clear, structured representation of the database schema.
        
        Args:
            schema_name: PostgreSQL schema name
        
        Returns:
            Formatted schema string suitable for LLM prompts
        """
        metadata = self.get_full_schema_metadata(schema_name)
        
        if not metadata['tables']:
            return f"Schema '{schema_name}' has no tables."
        
        output = [f"Database Schema: {schema_name}\n"]
        output.append("=" * 60)
        
        for table in metadata['tables']:
            table_name = table['table_name']
            row_count = table['row_count']
            full_table_name = f"{schema_name}.{table_name}"
            
            output.append(f"\nTable: {full_table_name} (~{row_count:,} rows)")
            output.append("-" * 60)
            
            for col in table['columns']:
                nullable = "NULL" if col['is_nullable'] else "NOT NULL"
                output.append(
                    f"  - {col['column_name']}: {col['data_type']} ({nullable})"
                )
        
        return "\n".join(output)
    
    def get_sample_data(
        self, 
        schema_name: str, 
        table_name: str, 
        limit: int = 3
    ) -> List[Dict]:
        """
        Get sample rows from a table (for schema understanding).
        
        Args:
            schema_name: Schema name
            table_name: Table name
            limit: Number of sample rows to retrieve
        
        Returns:
            List of row dictionaries
        """
        try:
            # Safely construct table reference
            full_table = f"{schema_name}.{table_name}"
            query = text(f"SELECT * FROM {full_table} LIMIT :limit")
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                columns = result.keys()
                
                samples = []
                for row in result:
                    samples.append(dict(zip(columns, row)))
                
                return samples
                
        except Exception as e:
            logger.error(f"Error fetching sample data: {str(e)}")
            return []
