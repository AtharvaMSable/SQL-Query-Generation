"""Prompts for SQL generation using LLM"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PromptTemplates:
    """Prompts for converting natural language to SQL"""
    
    @staticmethod
    def get_sql_generation_prompt(
        question: str,
        schema_context: str,
        dataset_name: str,
        user_role: str = "analyst"
    ) -> str:
        """Create prompt for SQL generation"""
        prompt = f"""You are a PostgreSQL query generator.
Your task is to convert natural language questions into SQL queries.

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
        """Create prompt for generating insights from query results"""
        prompt = f"""Generate a brief insight from this data query.

USER QUESTION:
{question}

SQL QUERY EXECUTED:
{sql_query}

RESULTS SUMMARY:
{results_summary}
Total rows: {row_count}

TASK:
Generate 2-3 sentences that:
1. Answer the user's question
2. Highlight key findings
3. Include specific numbers from results

Generate the insight:
"""
        return prompt
    
    @staticmethod
    def get_query_refinement_prompt(
        original_question: str,
        original_sql: str,
        error_message: str,
        schema_context: str
    ) -> str:
        """Create prompt for fixing failed SQL queries"""
        prompt = f"""Fix this SQL query.

ORIGINAL QUESTION:
{original_question}

FAILED SQL QUERY:
{original_sql}

ERROR MESSAGE:
{error_message}

DATABASE SCHEMA:
{schema_context}

TASK:
Fix the error and return a working SELECT query.

Return ONLY the corrected SQL query.
"""
        return prompt
    
    @staticmethod
    def get_chart_recommendation_prompt(
        question: str,
        columns: list,
        sample_data: str
    ) -> str:
        """Create prompt for chart type recommendation"""
        prompt = f"""Recommend a chart type for this data.

USER QUESTION:
{question}

RESULT COLUMNS:
{', '.join(columns)}

SAMPLE DATA:
{sample_data}

Chart options:
- bar (categorical comparisons)
- line (time series or trends)
- pie (part-to-whole, max 10 categories)
- scatter (correlation between numeric values)
- table (no visualization needed)

Respond with ONE WORD: the chart type (lowercase).
"""
        return prompt
    
    @staticmethod
    def create_system_prompt() -> str:
        """System prompt for LLM interactions"""
        return """You are AskQL Assistant. You convert natural language to PostgreSQL queries.

Guidelines:
- Generate correct SQL syntax
- Follow security practices
- Give concise responses
- Validate output

Never:
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
