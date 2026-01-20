"""
Chart Generator Module
Creates interactive Plotly visualizations from query results.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ChartGenerator:
    """
    Generates appropriate visualizations based on data characteristics.
    Uses Plotly for interactive charts.
    """
    
    @staticmethod
    def auto_generate_chart(
        df: pd.DataFrame,
        question: str = ""
    ) -> Tuple[Optional[go.Figure], str]:
        """
        Automatically determine and generate the most appropriate chart.
        
        Args:
            df: Query results as DataFrame
            question: Original user question (for context)
        
        Returns:
            Tuple of (Plotly figure or None, chart_type_name)
        """
        if df is None or df.empty:
            logger.warning("Cannot generate chart: DataFrame is empty")
            return None, "none"
        
        # Determine chart type based on data characteristics
        chart_type = ChartGenerator._determine_chart_type(df, question)
        
        logger.info(f"Auto-selected chart type: {chart_type}")
        
        # Generate the appropriate chart
        if chart_type == "bar":
            return ChartGenerator.create_bar_chart(df), "bar"
        elif chart_type == "line":
            return ChartGenerator.create_line_chart(df), "line"
        elif chart_type == "pie":
            return ChartGenerator.create_pie_chart(df), "pie"
        elif chart_type == "scatter":
            return ChartGenerator.create_scatter_chart(df), "scatter"
        else:
            return None, "table"
    
    @staticmethod
    def _determine_chart_type(df: pd.DataFrame, question: str = "") -> str:
        """
        Intelligently determine the best chart type for the data.
        
        Args:
            df: DataFrame to analyze
            question: User's question for additional context
        
        Returns:
            Chart type: 'bar', 'line', 'pie', 'scatter', or 'table'
        """
        num_rows = len(df)
        num_cols = len(df.columns)
        
        # If too many rows, default to table
        if num_rows > 100:
            return "table"
        
        # Need at least 2 columns for most charts
        if num_cols < 2:
            return "table"
        
        # Analyze column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Time series: line chart
        if len(date_cols) >= 1 and len(numeric_cols) >= 1:
            return "line"
        
        # Check question keywords for hints
        question_lower = question.lower()
        if any(word in question_lower for word in ['trend', 'over time', 'timeline', 'history']):
            return "line"
        if any(word in question_lower for word in ['distribution', 'breakdown', 'proportion', 'percentage']):
            if num_rows <= 10:
                return "pie"
        if any(word in question_lower for word in ['compare', 'comparison', 'top', 'bottom', 'ranking']):
            return "bar"
        
        # 1 categorical + 1 numeric = bar chart
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            if num_rows <= 20:
                return "bar"
        
        # 2+ numeric columns = scatter plot
        if len(numeric_cols) >= 2:
            return "scatter"
        
        # Part-to-whole with few categories = pie chart
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1 and num_rows <= 10:
            return "pie"
        
        # Default to bar chart for moderate data
        if num_rows <= 20:
            return "bar"
        
        return "table"
    
    @staticmethod
    def create_bar_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create an interactive bar chart.
        
        Args:
            df: DataFrame with data
        
        Returns:
            Plotly Figure or None
        """
        try:
            # Identify x and y columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                # Fallback: use first two columns
                x_col = df.columns[0]
                y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            else:
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
            
            # Sort by y value descending for better visualization
            df_sorted = df.sort_values(by=y_col, ascending=False).head(20)
            
            fig = px.bar(
                df_sorted,
                x=x_col,
                y=y_col,
                title=f"{y_col} by {x_col}",
                labels={x_col: str(x_col).replace('_', ' ').title(),
                        y_col: str(y_col).replace('_', ' ').title()},
                color=y_col,
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                xaxis_tickangle=-45,
                showlegend=False,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Bar chart generation error: {str(e)}")
            return None
    
    @staticmethod
    def create_line_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create an interactive line chart (typically for time series).
        
        Args:
            df: DataFrame with data
        
        Returns:
            Plotly Figure or None
        """
        try:
            # Identify date/time and numeric columns
            date_cols = df.select_dtypes(include=['datetime']).columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(date_cols) > 0:
                x_col = date_cols[0]
            else:
                # Use first column as x-axis
                x_col = df.columns[0]
            
            y_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[1]
            
            # Sort by x-axis for proper line rendering
            df_sorted = df.sort_values(by=x_col)
            
            fig = px.line(
                df_sorted,
                x=x_col,
                y=y_col,
                title=f"{y_col} over {x_col}",
                labels={x_col: str(x_col).replace('_', ' ').title(),
                        y_col: str(y_col).replace('_', ' ').title()},
                markers=True
            )
            
            fig.update_traces(line_color='#1f77b4', line_width=2)
            fig.update_layout(hovermode='x unified')
            
            return fig
            
        except Exception as e:
            logger.error(f"Line chart generation error: {str(e)}")
            return None
    
    @staticmethod
    def create_pie_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create an interactive pie chart for part-to-whole relationships.
        
        Args:
            df: DataFrame with data
        
        Returns:
            Plotly Figure or None
        """
        try:
            # Identify categorical and numeric columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                names_col = df.columns[0]
                values_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            else:
                names_col = categorical_cols[0]
                values_col = numeric_cols[0]
            
            # Limit to top 10 categories for readability
            df_top = df.nlargest(10, values_col)
            
            fig = px.pie(
                df_top,
                names=names_col,
                values=values_col,
                title=f"Distribution of {values_col}",
                hole=0.3  # Donut chart style
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            return fig
            
        except Exception as e:
            logger.error(f"Pie chart generation error: {str(e)}")
            return None
    
    @staticmethod
    def create_scatter_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create an interactive scatter plot for correlation analysis.
        
        Args:
            df: DataFrame with data
        
        Returns:
            Plotly Figure or None
        """
        try:
            # Use first two numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) < 2:
                # Fallback to first two columns
                x_col = df.columns[0]
                y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            else:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
            
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                title=f"{y_col} vs {x_col}",
                labels={x_col: str(x_col).replace('_', ' ').title(),
                        y_col: str(y_col).replace('_', ' ').title()},
                trendline="ols"  # Add trend line
            )
            
            fig.update_traces(marker=dict(size=8, opacity=0.7))
            
            return fig
            
        except Exception as e:
            logger.error(f"Scatter chart generation error: {str(e)}")
            return None
    
    @staticmethod
    def create_custom_chart(
        df: pd.DataFrame,
        chart_type: str,
        x_col: str,
        y_col: str,
        title: str = None
    ) -> Optional[go.Figure]:
        """
        Create a custom chart with specific parameters.
        
        Args:
            df: DataFrame with data
            chart_type: Type of chart ('bar', 'line', 'scatter', 'pie')
            x_col: Column name for x-axis
            y_col: Column name for y-axis
            title: Optional chart title
        
        Returns:
            Plotly Figure or None
        """
        try:
            if chart_type == "bar":
                fig = px.bar(df, x=x_col, y=y_col, title=title)
            elif chart_type == "line":
                fig = px.line(df, x=x_col, y=y_col, title=title)
            elif chart_type == "scatter":
                fig = px.scatter(df, x=x_col, y=y_col, title=title)
            elif chart_type == "pie":
                fig = px.pie(df, names=x_col, values=y_col, title=title)
            else:
                return None
            
            return fig
            
        except Exception as e:
            logger.error(f"Custom chart generation error: {str(e)}")
            return None
