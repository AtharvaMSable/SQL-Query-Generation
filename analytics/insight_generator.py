"""
Insight Generator Module
Generates AI-powered insights from query results.
"""

import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Generates business insights from query results.
    Combines statistical analysis with LLM-generated narratives.
    """
    
    @staticmethod
    def generate_summary_stats(df: pd.DataFrame) -> str:
        """
        Generate summary statistics from DataFrame.
        
        Args:
            df: Query results DataFrame
        
        Returns:
            Formatted summary statistics string
        """
        if df is None or df.empty:
            return "No data available for analysis."
        
        try:
            summary_parts = []
            
            # Basic info
            summary_parts.append(f"Total records: {len(df):,}")
            summary_parts.append(f"Columns: {len(df.columns)}")
            
            # Numeric column statistics
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                col_data = df[col].dropna()
                
                if len(col_data) > 0:
                    stats = [
                        f"\n{col}:",
                        f"  - Mean: {col_data.mean():.2f}",
                        f"  - Median: {col_data.median():.2f}",
                        f"  - Min: {col_data.min():.2f}",
                        f"  - Max: {col_data.max():.2f}",
                        f"  - Std Dev: {col_data.std():.2f}"
                    ]
                    summary_parts.extend(stats)
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Summary stats generation error: {str(e)}")
            return "Unable to generate summary statistics."
    
    @staticmethod
    def create_results_summary_for_llm(df: pd.DataFrame, max_rows: int = 10) -> str:
        """
        Create a concise summary of results for LLM consumption.
        
        Args:
            df: Query results DataFrame
            max_rows: Maximum rows to include in summary
        
        Returns:
            Formatted summary string
        """
        if df is None or df.empty:
            return "No results returned."
        
        try:
            summary = []
            
            # Include column names
            summary.append(f"Columns: {', '.join(df.columns)}")
            summary.append(f"Total rows: {len(df)}\n")
            
            # Include sample of top rows
            summary.append("Top rows:")
            for idx, row in df.head(max_rows).iterrows():
                row_str = " | ".join([f"{col}: {val}" for col, val in row.items()])
                summary.append(f"  {row_str}")
            
            # Include basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary.append("\nNumeric summaries:")
                for col in numeric_cols[:3]:
                    col_mean = df[col].mean()
                    col_sum = df[col].sum()
                    summary.append(f"  {col}: Mean={col_mean:.2f}, Total={col_sum:.2f}")
            
            return "\n".join(summary)
            
        except Exception as e:
            logger.error(f"Results summary creation error: {str(e)}")
            return "Unable to create results summary."
    
    @staticmethod
    def detect_trends(df: pd.DataFrame) -> Optional[str]:
        """
        Detect trends in time-series or numeric data.
        
        Args:
            df: Query results DataFrame
        
        Returns:
            Trend description or None
        """
        if df is None or df.empty:
            return None
        
        try:
            # Look for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) == 0:
                return None
            
            # Analyze first numeric column for trend
            col = numeric_cols[0]
            values = df[col].dropna()
            
            if len(values) < 3:
                return None
            
            # Simple trend detection: compare first half vs second half
            mid_point = len(values) // 2
            first_half_avg = values[:mid_point].mean()
            second_half_avg = values[mid_point:].mean()
            
            change_pct = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            
            if abs(change_pct) < 5:
                trend = "stable"
            elif change_pct > 0:
                trend = f"increasing by {change_pct:.1f}%"
            else:
                trend = f"decreasing by {abs(change_pct):.1f}%"
            
            return f"Trend: {col} is {trend}"
            
        except Exception as e:
            logger.error(f"Trend detection error: {str(e)}")
            return None
    
    @staticmethod
    def find_outliers(df: pd.DataFrame) -> Optional[str]:
        """
        Identify outliers in numeric data using IQR method.
        
        Args:
            df: Query results DataFrame
        
        Returns:
            Outlier description or None
        """
        if df is None or df.empty:
            return None
        
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) == 0:
                return None
            
            outlier_info = []
            
            for col in numeric_cols[:2]:  # Analyze first 2 numeric columns
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                if len(outliers) > 0:
                    outlier_info.append(
                        f"{col}: {len(outliers)} outlier(s) detected "
                        f"(range: {lower_bound:.2f} - {upper_bound:.2f})"
                    )
            
            return "\n".join(outlier_info) if outlier_info else None
            
        except Exception as e:
            logger.error(f"Outlier detection error: {str(e)}")
            return None
    
    @staticmethod
    def get_top_insights(df: pd.DataFrame) -> list:
        """
        Get a list of key insights from the data.
        
        Args:
            df: Query results DataFrame
        
        Returns:
            List of insight strings
        """
        insights = []
        
        if df is None or df.empty:
            return ["No data available for insights."]
        
        try:
            # Row count insight
            if len(df) > 0:
                insights.append(f"📊 Found {len(df):,} records")
            
            # Top value insight (for categorical data)
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                top_value = df[col].value_counts().iloc[0]
                top_name = df[col].value_counts().index[0]
                insights.append(f"🏆 Top {col}: {top_name} ({top_value} occurrences)")
            
            # Numeric insights
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                total = df[col].sum()
                avg = df[col].mean()
                insights.append(f"💰 {col} - Total: {total:,.2f}, Average: {avg:,.2f}")
            
            # Trend insight
            trend = InsightGenerator.detect_trends(df)
            if trend:
                insights.append(f"📈 {trend}")
            
            return insights[:4]  # Return top 4 insights
            
        except Exception as e:
            logger.error(f"Top insights generation error: {str(e)}")
            return ["Unable to generate insights from this data."]
    
    @staticmethod
    def format_insights_for_display(insights: list) -> str:
        """
        Format insights list as a readable string.
        
        Args:
            insights: List of insight strings
        
        Returns:
            Formatted insights string
        """
        if not insights:
            return "No insights available."
        
        return "\n\n".join(insights)
