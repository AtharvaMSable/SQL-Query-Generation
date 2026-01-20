"""
Prompt Templates for LLM
Contains carefully engineered prompts for SQL generation.
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PromptTemplates:
    """
    Centralized prompt templates for different LLM tasks.
    Uses advanced prompt engineering techniques for reliable SQL generation.
    """
    
    @staticmethod
    def get_sql_generation_prompt(
        question: str,
        schema_context: str,
        dataset_name: str,
        user_role: str = "analyst"
    ) -> str:
        """
        Generate a comprehensive prompt for SQL generation.
        
        Args:
            question: User's natural language question
            schema_context: Formatted database schema information
            dataset_name: Name of the dataset being queried
            user_role: User's role (for context)
        
        Returns:
            Complete prompt string for the LLM
        """
        prompt = f"""You are an expert PostgreSQL query generator for a business analytics platform.
Your task is to convert natural language questions into safe, efficient SQL queries.

CONTEXT:
- Dataset: {dataset_name}
- User Role: {user_role}
- Database: PostgreSQL (Neon serverless)

DATABASE SCHEMA:
{schema_context}

STRICT RULES:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE)
2. Use proper PostgreSQL syntax
3. ALWAYS use the full table name with schema prefix (e.g., sales_data.products, not just products)
4. Apply appropriate WHERE clauses for filtering
5. Use appropriate aggregation functions (COUNT, SUM, AVG, MAX, MIN) when needed
6. Include GROUP BY when using aggregate functions with non-aggregated columns
7. Add ORDER BY for sorting results logically
8. Never use LIMIT in your response (it will be added automatically)
9. Handle date/time queries using PostgreSQL date functions
10. Use JOINs appropriately when querying multiple tables
11. Return ONLY the SQL query - no explanations, no markdown formatting, no comments
12. Ensure query is syntactically correct and executable
13. Use meaningful column aliases for complex expressions
14. When using table aliases, use simple names (e.g., 'p' for products, 's' for sales), not 'sd.products'

QUERY OPTIMIZATION GUIDELINES:
- Prefer indexed columns in WHERE clauses when possible
- Avoid SELECT * - specify only needed columns
- Use EXISTS instead of COUNT(*) > 0 for existence checks
- Be mindful of NULL values in comparisons

USER QUESTION:
{question}

Generate the PostgreSQL SELECT query that answers this question.
Return ONLY the raw SQL query, nothing else.
"""
        return prompt
    
    @staticmethod
    def get_insight_generation_prompt(
        question: str,
        sql_query: str,
        results_summary: str,
        row_count: int
    ) -> str:
        """
        Generate prompt for creating business insights from query results.
        
        Args:
            question: Original user question
            sql_query: SQL query that was executed
            results_summary: Summary of the results (top rows, statistics)
            row_count: Number of rows returned
        
        Returns:
            Prompt for insight generation
        """
        prompt = f"""You are a business analytics expert providing insights from data.

USER QUESTION:
{question}

SQL QUERY EXECUTED:
{sql_query}

RESULTS SUMMARY:
{results_summary}
Total rows: {row_count}

TASK:
Generate a concise, business-friendly insight (2-3 sentences) that:
1. Directly answers the user's question
2. Highlights key findings or trends
3. Provides actionable takeaways if applicable
4. Uses specific numbers from the results
5. Is written for non-technical business users

Generate the insight now:
"""
        return prompt
    
    @staticmethod
    def get_query_refinement_prompt(
        original_question: str,
        original_sql: str,
        error_message: str,
        schema_context: str
    ) -> str:
        """
        Generate prompt for fixing a failed SQL query.
        
        Args:
            original_question: User's question
            original_sql: SQL that failed
            error_message: Error from database
            schema_context: Schema information
        
        Returns:
            Prompt for query refinement
        """
        prompt = f"""You are a PostgreSQL expert fixing a failed query.

ORIGINAL QUESTION:
{original_question}

FAILED SQL QUERY:
{original_sql}

ERROR MESSAGE:
{error_message}

DATABASE SCHEMA:
{schema_context}

TASK:
Analyze the error and generate a corrected SQL query that:
1. Fixes the specific error mentioned
2. Still answers the original question
3. Follows all PostgreSQL syntax rules
4. Is a valid SELECT query

Return ONLY the corrected SQL query, nothing else.
"""
        return prompt
    
    @staticmethod
    def get_chart_recommendation_prompt(
        question: str,
        columns: list,
        sample_data: str
    ) -> str:
        """
        Generate prompt for recommending chart type.
        
        Args:
            question: User's question
            columns: List of column names in results
            sample_data: Sample of the data
        
        Returns:
            Prompt for chart recommendation
        """
        prompt = f"""You are a data visualization expert.

USER QUESTION:
{question}

RESULT COLUMNS:
{', '.join(columns)}

SAMPLE DATA:
{sample_data}

TASK:
Recommend the most appropriate chart type from these options:
- bar (for categorical comparisons)
- line (for time series or trends)
- pie (for part-to-whole relationships, max 10 categories)
- scatter (for correlation between two numeric variables)
- table (when visualization doesn't add value)

Respond with ONLY ONE WORD: the chart type name (lowercase).
"""
        return prompt
    
    @staticmethod
    def create_system_prompt() -> str:
        """
        Create a consistent system prompt for all interactions.
        
        Returns:
            System prompt string
        """
        return """You are AskQL Assistant, an expert AI system specialized in:
1. Converting natural language to SQL (PostgreSQL)
2. Analyzing data and generating business insights
3. Ensuring query safety and data security

You ALWAYS:
- Generate syntactically correct SQL
- Follow security best practices
- Provide concise, accurate responses
- Think step-by-step for complex queries
- Validate your output before responding

You NEVER:
- Generate destructive queries (DELETE, UPDATE, DROP, etc.)
- Include explanatory text when only SQL is requested
- Make assumptions about missing schema information
- Produce queries that could harm data integrity
"""
    
    @staticmethod
    def get_sql_explanation_prompt(sql_query: str) -> str:
        """
        Generate prompt for explaining SQL query in business terms.
        
        Args:
            sql_query: SQL query to explain
        
        Returns:
            Prompt for SQL explanation
        """
        prompt = f"""Explain the following SQL query in simple business terms for non-technical users.

SQL QUERY:
{sql_query}

Provide a 1-2 sentence explanation that describes:
- What data is being retrieved
- Any filters or conditions applied
- How the data is organized or aggregated

Use plain English, avoid technical jargon.
"""
        return prompt
    
    @staticmethod
    def format_schema_context_enhanced(schema_metadata: Dict) -> str:
        """
        Format schema with additional context hints for better SQL generation.
        
        Args:
            schema_metadata: Schema metadata dictionary
        
        Returns:
            Enhanced schema context string
        """
        output = []
        
        for table in schema_metadata.get('tables', []):
            table_name = table['table_name']
            output.append(f"\nTable: {table_name}")
            
            # Add column information
            columns = []
            for col in table['columns']:
                col_info = f"{col['column_name']} ({col['data_type']})"
                columns.append(col_info)
            
            output.append("Columns: " + ", ".join(columns))
        
        return "\n".join(output)
