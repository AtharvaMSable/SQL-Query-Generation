"""
AskQL - AI-Powered Analytics Platform
Main Streamlit Application Entry Point

Production-grade natural language to SQL query system with:
- Multi-tenant authentication
- Schema-aware SQL generation via Gemini
- Comprehensive SQL validation
- Interactive visualizations
- AI-generated insights
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import traceback

# Import application modules
from config.settings import settings
from config.database_config import DatabaseConfig
from auth.user_auth import UserAuth
from auth.session_manager import SessionManager
from database.schema_loader import SchemaLoader
from database.query_executor import QueryExecutor
from llm.gemini_client import GeminiClient
from analytics.chart_generator import ChartGenerator
from analytics.insight_generator import InsightGenerator
from utils.logger import setup_logger, get_logger
from utils.helpers import format_sql_for_display, truncate_text

# Initialize logger
logger = setup_logger('askql')

# Configure Streamlit page
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)


def validate_environment():
    """Validate that all required configuration is present."""
    try:
        settings.validate()
        logger.info("Environment validation successful")
        return True
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {str(e)}")
        st.info("Please check your .env file and ensure all required variables are set.")
        logger.error(f"Environment validation failed: {str(e)}")
        return False


def show_login_page():
    """Display login page and handle authentication."""
    st.title("🤖 AskQL Analytics Platform")
    st.markdown("### AI-Powered Natural Language Query System")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        auth = UserAuth()
                        user_info = auth.authenticate_user(username, password)
                        
                        if user_info:
                            SessionManager.login(user_info)
                            st.success(f"✅ Welcome, {user_info['full_name']}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please try again.")
        
        st.markdown("---")
        st.caption("🔒 Secure multi-tenant authentication")
        st.caption("💡 Demo credentials available in database setup")


def show_sidebar():
    """Display sidebar with user info and dataset selector."""
    with st.sidebar:
        user_info = SessionManager.get_user_info()
        
        # User info section
        st.markdown("### 👤 User Information")
        st.write(f"**Name:** {user_info['full_name']}")
        st.write(f"**Role:** {user_info['role']}")
        st.write(f"**Email:** {user_info['email']}")
        
        st.markdown("---")
        
        # Dataset selector
        st.markdown("### 📊 Select Dataset")
        
        auth = UserAuth()
        datasets = auth.get_user_datasets(user_info['user_id'])
        
        if not datasets:
            st.warning("No datasets available for your account.")
            st.info("Contact your administrator to request dataset access.")
            return
        
        dataset_options = {ds['dataset_name']: ds for ds in datasets}
        
        selected_dataset_name = st.selectbox(
            "Available Datasets",
            options=list(dataset_options.keys()),
            format_func=lambda x: f"{x} ({dataset_options[x]['access_level']})"
        )
        
        if selected_dataset_name:
            selected_dataset = dataset_options[selected_dataset_name]
            SessionManager.set_selected_dataset(selected_dataset)
            
            st.success(f"✅ Using: {selected_dataset_name}")
            
            with st.expander("📋 Dataset Info"):
                st.write(f"**Schema:** {selected_dataset['schema_name']}")
                st.write(f"**Description:** {selected_dataset['description']}")
                st.write(f"**Access Level:** {selected_dataset['access_level']}")
        
        st.markdown("---")
        
        # Query history
        history = SessionManager.get_query_history()
        if history:
            st.markdown("### 📜 Recent Queries")
            for i, query in enumerate(reversed(history[-5:])):
                with st.expander(f"Query {len(history) - i}"):
                    st.caption(query['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
                    st.text(truncate_text(query['question'], 80))
                    st.caption(f"Rows: {query['row_count']}")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            SessionManager.logout()
            st.rerun()


def show_main_app():
    """Display main application interface."""
    st.title("🤖 AskQL Analytics")
    st.markdown("Ask questions in plain English, get insights backed by data.")
    
    # Check if dataset is selected
    dataset = SessionManager.get_selected_dataset()
    if not dataset:
        st.warning("⚠️ Please select a dataset from the sidebar to begin.")
        return
    
    # Main query interface
    st.markdown("---")
    
    # Question input
    question = st.text_area(
        "💬 What would you like to know?",
        placeholder="Example: What were the top 5 products by revenue last month?",
        height=100,
        key="question_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        SessionManager.clear_results()
        st.rerun()
    
    # Process query
    if analyze_button and question:
        process_query(question, dataset)
    
    # Display results if available
    results = SessionManager.get_current_results()
    if results:
        display_results(results)


def process_query(question: str, dataset: dict):
    """
    Process natural language question and generate results.
    
    Args:
        question: User's natural language question
        dataset: Selected dataset information
    """
    try:
        # Initialize components
        schema_loader = SchemaLoader()
        query_executor = QueryExecutor()
        gemini_client = GeminiClient()
        
        schema_name = dataset['schema_name']
        
        with st.spinner("🧠 Understanding your question..."):
            # Load schema context
            schema_context = schema_loader.format_schema_for_llm(schema_name)
            
            if not schema_context or "has no tables" in schema_context:
                st.error(f"❌ No tables found in schema: {schema_name}")
                logger.error(f"Empty schema: {schema_name}")
                return
        
        with st.spinner("⚙️ Generating SQL query..."):
            # Generate SQL using Gemini
            sql, error = gemini_client.generate_sql(
                question=question,
                schema_context=schema_context,
                dataset_name=dataset['dataset_name'],
                user_role=SessionManager.get_user_role()
            )
            
            if error or not sql:
                st.error(f"❌ Failed to generate SQL: {error}")
                logger.error(f"SQL generation failed: {error}")
                return
        
        # Display generated SQL
        with st.expander("🔍 View Generated SQL", expanded=False):
            st.code(format_sql_for_display(sql), language="sql")
        
        with st.spinner("📊 Executing query..."):
            # Execute query
            df, exec_error = query_executor.execute_query(
                sql=sql,
                allowed_schema=schema_name
            )
            
            if exec_error or df is None:
                st.error(f"❌ Query execution failed: {exec_error}")
                logger.error(f"Query execution error: {exec_error}")
                
                # Attempt to refine the query
                with st.spinner("🔄 Attempting to fix query..."):
                    refined_sql, refine_error = gemini_client.refine_sql(
                        original_question=question,
                        original_sql=sql,
                        error_message=exec_error,
                        schema_context=schema_context
                    )
                    
                    if refined_sql and not refine_error:
                        st.info("🔄 Retrying with refined query...")
                        df, exec_error = query_executor.execute_query(
                            sql=refined_sql,
                            allowed_schema=schema_name
                        )
                        
                        if df is not None:
                            st.success("✅ Query succeeded after refinement!")
                            sql = refined_sql
                        else:
                            st.error(f"❌ Refined query also failed: {exec_error}")
                            return
                    else:
                        return
        
        # Check if results are empty
        if df.empty:
            st.warning("⚠️ Query executed successfully but returned no results.")
            st.info("Try rephrasing your question or check if the data exists.")
            return
        
        with st.spinner("🎨 Generating visualizations and insights..."):
            # Generate chart
            chart, chart_type = ChartGenerator.auto_generate_chart(df, question)
            
            # Generate insights
            insight_gen = InsightGenerator()
            quick_insights = insight_gen.get_top_insights(df)
            
            # Generate AI insights
            results_summary = insight_gen.create_results_summary_for_llm(df)
            ai_insight = gemini_client.generate_insights(
                question=question,
                sql_query=sql,
                results_summary=results_summary,
                row_count=len(df)
            )
        
        # Store results in session
        results = {
            'question': question,
            'sql': sql,
            'dataframe': df,
            'chart': chart,
            'chart_type': chart_type,
            'quick_insights': quick_insights,
            'ai_insight': ai_insight,
            'timestamp': datetime.now()
        }
        
        SessionManager.set_current_results(results)
        SessionManager.add_query_to_history(question, sql, df)
        
        # Log to database
        user_id = SessionManager.get_user_id()
        auth = UserAuth()
        auth.log_query_history(
            user_id=user_id,
            dataset_id=dataset['dataset_id'],
            question=question,
            generated_sql=sql,
            row_count=len(df)
        )
        
        st.success("✅ Analysis complete!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        logger.error(f"Query processing error: {str(e)}\n{traceback.format_exc()}")


def display_results(results: dict):
    """
    Display query results with visualizations and insights.
    
    Args:
        results: Dictionary containing query results and metadata
    """
    st.markdown("---")
    st.markdown("## 📊 Results")
    
    # Quick insights
    if results.get('quick_insights'):
        st.markdown("### 💡 Quick Insights")
        for insight in results['quick_insights']:
            st.info(insight)
    
    # AI-generated insight
    if results.get('ai_insight'):
        st.markdown("### 🤖 AI Analysis")
        st.success(results['ai_insight'])
    
    st.markdown("---")
    
    # Visualization
    if results.get('chart'):
        st.markdown("### 📈 Visualization")
        st.plotly_chart(results['chart'], use_container_width=True)
    
    # Data table
    st.markdown("### 📋 Data")
    df = results['dataframe']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))
    col3.metric("Chart Type", results.get('chart_type', 'table').title())
    
    st.dataframe(df, use_container_width=True, height=400)
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"askql_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # SQL preview
    with st.expander("🔍 View SQL Query"):
        st.code(format_sql_for_display(results['sql']), language="sql")


def main():
    """Main application entry point."""
    # Validate environment configuration
    if not validate_environment():
        st.stop()
    
    # Test database connection
    if not DatabaseConfig.test_connection():
        st.error("❌ Failed to connect to database. Please check your configuration.")
        st.info(f"Database URL: {settings.NEON_DB_URL[:50]}...")
        st.stop()
    
    # Initialize session state
    SessionManager.initialize_session()
    
    # Check session timeout
    if SessionManager.is_authenticated():
        if not SessionManager.check_session_timeout():
            st.warning("⚠️ Your session has expired. Please log in again.")
            st.rerun()
    
    # Route to appropriate page
    if not SessionManager.is_authenticated():
        show_login_page()
    else:
        show_sidebar()
        show_main_app()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}\n{traceback.format_exc()}")
        st.error(f"❌ Application Error: {str(e)}")
        st.info("Please check the logs for more details.")
