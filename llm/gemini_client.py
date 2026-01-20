"""
Gemini Client Module
Handles communication with Google Gemini API for SQL generation and insights.
"""

import google.generativeai as genai
from typing import Optional, Tuple
import logging
import time

from config.settings import settings
from .prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for interacting with Google Gemini API.
    Handles prompt construction, API calls, and response parsing.
    """
    
    def __init__(self):
        """Initialize Gemini client with API key from settings."""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.prompt_templates = PromptTemplates()
            logger.info(f"Gemini client initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise
    
    def generate_sql(
        self,
        question: str,
        schema_context: str,
        dataset_name: str,
        user_role: str = "analyst"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate SQL query from natural language question.
        
        Args:
            question: User's natural language question
            schema_context: Formatted database schema
            dataset_name: Name of the dataset
            user_role: User's role for context
        
        Returns:
            Tuple of (sql_query or None, error_message or None)
            On success: (sql_query, None)
            On error: (None, error_message)
        """
        try:
            # Build the prompt
            prompt = self.prompt_templates.get_sql_generation_prompt(
                question=question,
                schema_context=schema_context,
                dataset_name=dataset_name,
                user_role=user_role
            )
            
            logger.info(f"Generating SQL for question: {question[:100]}...")
            
            # Call Gemini API with timeout and retry logic
            sql_query = self._call_gemini_with_retry(prompt)
            
            if not sql_query:
                return None, "Failed to generate SQL query"
            
            # Clean up the response
            sql_query = self._clean_sql_response(sql_query)
            
            logger.info(f"SQL generated successfully: {sql_query[:100]}...")
            return sql_query, None
            
        except Exception as e:
            error_msg = f"SQL generation error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def generate_insights(
        self,
        question: str,
        sql_query: str,
        results_summary: str,
        row_count: int
    ) -> Optional[str]:
        """
        Generate business insights from query results.
        
        Args:
            question: Original user question
            sql_query: SQL that was executed
            results_summary: Summary of results
            row_count: Number of rows returned
        
        Returns:
            Generated insight string or None on error
        """
        try:
            prompt = self.prompt_templates.get_insight_generation_prompt(
                question=question,
                sql_query=sql_query,
                results_summary=results_summary,
                row_count=row_count
            )
            
            logger.info("Generating insights from results...")
            
            insight = self._call_gemini_with_retry(prompt)
            
            if insight:
                # Clean up any markdown formatting
                insight = insight.strip().replace('**', '').replace('*', '')
                logger.info("Insights generated successfully")
                return insight
            
            return None
            
        except Exception as e:
            logger.error(f"Insight generation error: {str(e)}")
            return None
    
    def refine_sql(
        self,
        original_question: str,
        original_sql: str,
        error_message: str,
        schema_context: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Attempt to fix a failed SQL query.
        
        Args:
            original_question: User's question
            original_sql: SQL that failed
            error_message: Database error
            schema_context: Schema information
        
        Returns:
            Tuple of (refined_sql or None, error_message or None)
        """
        try:
            prompt = self.prompt_templates.get_query_refinement_prompt(
                original_question=original_question,
                original_sql=original_sql,
                error_message=error_message,
                schema_context=schema_context
            )
            
            logger.info("Attempting to refine failed SQL query...")
            
            refined_sql = self._call_gemini_with_retry(prompt)
            
            if not refined_sql:
                return None, "Failed to refine SQL query"
            
            refined_sql = self._clean_sql_response(refined_sql)
            
            logger.info("SQL refinement successful")
            return refined_sql, None
            
        except Exception as e:
            error_msg = f"SQL refinement error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def explain_sql(self, sql_query: str) -> Optional[str]:
        """
        Generate plain English explanation of SQL query.
        
        Args:
            sql_query: SQL query to explain
        
        Returns:
            Explanation string or None on error
        """
        try:
            prompt = self.prompt_templates.get_sql_explanation_prompt(sql_query)
            
            explanation = self._call_gemini_with_retry(prompt)
            
            if explanation:
                return explanation.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"SQL explanation error: {str(e)}")
            return None
    
    def _call_gemini_with_retry(
        self,
        prompt: str,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Call Gemini API with retry logic for transient failures.
        
        Args:
            prompt: Prompt to send to Gemini
            max_retries: Maximum number of retry attempts
        
        Returns:
            Generated text or None on failure
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Generate content with configured parameters
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=settings.LLM_TEMPERATURE,
                        max_output_tokens=settings.LLM_MAX_TOKENS,
                    ),
                    request_options={'timeout': settings.LLM_TIMEOUT_SECONDS}
                )
                
                # Extract text from response
                if response and response.text:
                    return response.text
                
                logger.warning(f"Empty response from Gemini on attempt {attempt + 1}")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Gemini API call failed on attempt {attempt + 1}: {last_error}"
                )
                
                # Exponential backoff for retries
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(sleep_time)
        
        logger.error(f"All Gemini API retry attempts failed. Last error: {last_error}")
        return None
    
    @staticmethod
    def _clean_sql_response(sql: str) -> str:
        """
        Clean SQL response from LLM output.
        Removes markdown formatting, extra whitespace, etc.
        
        Args:
            sql: Raw SQL from LLM
        
        Returns:
            Cleaned SQL string
        """
        # Remove markdown code blocks
        if '```sql' in sql:
            sql = sql.split('```sql')[1].split('```')[0]
        elif '```' in sql:
            sql = sql.split('```')[1].split('```')[0]
        
        # Remove any leading/trailing whitespace
        sql = sql.strip()
        
        # Remove trailing semicolon if present (will be added later if needed)
        if sql.endswith(';'):
            sql = sql[:-1]
        
        # Normalize whitespace
        sql = ' '.join(sql.split())
        
        return sql
    
    def test_connection(self) -> bool:
        """
        Test if Gemini API is accessible.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_prompt = "Respond with: OK"
            response = self._call_gemini_with_retry(test_prompt, max_retries=1)
            
            if response:
                logger.info("Gemini API connection test successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {str(e)}")
            return False
