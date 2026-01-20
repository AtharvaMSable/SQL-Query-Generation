"""
Session Manager
Handles Streamlit session state for user authentication and application state.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages user session state in Streamlit.
    Handles login state, user info, dataset selection, and query history.
    """
    
    # Session state keys
    KEY_AUTHENTICATED = 'authenticated'
    KEY_USER_INFO = 'user_info'
    KEY_LOGIN_TIME = 'login_time'
    KEY_SELECTED_DATASET = 'selected_dataset'
    KEY_QUERY_HISTORY = 'query_history'
    KEY_CURRENT_RESULTS = 'current_results'
    
    @staticmethod
    def initialize_session():
        """
        Initialize session state with default values.
        Called at app startup.
        """
        if SessionManager.KEY_AUTHENTICATED not in st.session_state:
            st.session_state[SessionManager.KEY_AUTHENTICATED] = False
        
        if SessionManager.KEY_USER_INFO not in st.session_state:
            st.session_state[SessionManager.KEY_USER_INFO] = None
        
        if SessionManager.KEY_LOGIN_TIME not in st.session_state:
            st.session_state[SessionManager.KEY_LOGIN_TIME] = None
        
        if SessionManager.KEY_SELECTED_DATASET not in st.session_state:
            st.session_state[SessionManager.KEY_SELECTED_DATASET] = None
        
        if SessionManager.KEY_QUERY_HISTORY not in st.session_state:
            st.session_state[SessionManager.KEY_QUERY_HISTORY] = []
        
        if SessionManager.KEY_CURRENT_RESULTS not in st.session_state:
            st.session_state[SessionManager.KEY_CURRENT_RESULTS] = None
    
    @staticmethod
    def login(user_info: Dict[str, Any]):
        """
        Set user as logged in and store user information.
        
        Args:
            user_info: Dictionary containing user details
        """
        st.session_state[SessionManager.KEY_AUTHENTICATED] = True
        st.session_state[SessionManager.KEY_USER_INFO] = user_info
        st.session_state[SessionManager.KEY_LOGIN_TIME] = datetime.now()
        logger.info(f"User logged in: {user_info.get('username')}")
    
    @staticmethod
    def logout():
        """
        Clear all session state and log out user.
        """
        username = SessionManager.get_username()
        
        # Clear all session state
        st.session_state[SessionManager.KEY_AUTHENTICATED] = False
        st.session_state[SessionManager.KEY_USER_INFO] = None
        st.session_state[SessionManager.KEY_LOGIN_TIME] = None
        st.session_state[SessionManager.KEY_SELECTED_DATASET] = None
        st.session_state[SessionManager.KEY_QUERY_HISTORY] = []
        st.session_state[SessionManager.KEY_CURRENT_RESULTS] = None
        
        logger.info(f"User logged out: {username}")
    
    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if user is authenticated.
        
        Returns:
            True if user is logged in, False otherwise
        """
        return st.session_state.get(SessionManager.KEY_AUTHENTICATED, False)
    
    @staticmethod
    def check_session_timeout() -> bool:
        """
        Check if session has timed out.
        
        Returns:
            True if session is still valid, False if timed out
        """
        if not SessionManager.is_authenticated():
            return False
        
        login_time = st.session_state.get(SessionManager.KEY_LOGIN_TIME)
        if not login_time:
            return False
        
        # Check if session has expired
        timeout_minutes = settings.SESSION_TIMEOUT_MINUTES
        time_elapsed = datetime.now() - login_time
        
        if time_elapsed > timedelta(minutes=timeout_minutes):
            logger.warning(f"Session timeout for user: {SessionManager.get_username()}")
            SessionManager.logout()
            return False
        
        return True
    
    @staticmethod
    def get_user_info() -> Optional[Dict[str, Any]]:
        """
        Get current user information.
        
        Returns:
            User info dictionary or None if not logged in
        """
        return st.session_state.get(SessionManager.KEY_USER_INFO)
    
    @staticmethod
    def get_user_id() -> Optional[int]:
        """Get current user's ID."""
        user_info = SessionManager.get_user_info()
        return user_info.get('user_id') if user_info else None
    
    @staticmethod
    def get_username() -> Optional[str]:
        """Get current user's username."""
        user_info = SessionManager.get_user_info()
        return user_info.get('username') if user_info else None
    
    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get current user's role."""
        user_info = SessionManager.get_user_info()
        return user_info.get('role') if user_info else None
    
    @staticmethod
    def set_selected_dataset(dataset: Dict[str, Any]):
        """
        Set the currently selected dataset.
        
        Args:
            dataset: Dataset information dictionary
        """
        st.session_state[SessionManager.KEY_SELECTED_DATASET] = dataset
        logger.info(
            f"Dataset selected: {dataset.get('dataset_name')} "
            f"by user: {SessionManager.get_username()}"
        )
    
    @staticmethod
    def get_selected_dataset() -> Optional[Dict[str, Any]]:
        """
        Get currently selected dataset.
        
        Returns:
            Dataset info dictionary or None
        """
        return st.session_state.get(SessionManager.KEY_SELECTED_DATASET)
    
    @staticmethod
    def add_query_to_history(question: str, sql: str, results: Any):
        """
        Add a query to the session history.
        
        Args:
            question: Natural language question
            sql: Generated SQL query
            results: Query results (DataFrame)
        """
        history = st.session_state.get(SessionManager.KEY_QUERY_HISTORY, [])
        
        history.append({
            'timestamp': datetime.now(),
            'question': question,
            'sql': sql,
            'row_count': len(results) if results is not None else 0,
        })
        
        # Keep only last 10 queries in memory
        if len(history) > 10:
            history = history[-10:]
        
        st.session_state[SessionManager.KEY_QUERY_HISTORY] = history
    
    @staticmethod
    def get_query_history() -> list:
        """
        Get query history for current session.
        
        Returns:
            List of query history dictionaries
        """
        return st.session_state.get(SessionManager.KEY_QUERY_HISTORY, [])
    
    @staticmethod
    def set_current_results(results: Any):
        """
        Store current query results.
        
        Args:
            results: Query results to store
        """
        st.session_state[SessionManager.KEY_CURRENT_RESULTS] = results
    
    @staticmethod
    def get_current_results() -> Any:
        """
        Get current query results.
        
        Returns:
            Stored query results or None
        """
        return st.session_state.get(SessionManager.KEY_CURRENT_RESULTS)
    
    @staticmethod
    def clear_results():
        """Clear current results from session."""
        st.session_state[SessionManager.KEY_CURRENT_RESULTS] = None
