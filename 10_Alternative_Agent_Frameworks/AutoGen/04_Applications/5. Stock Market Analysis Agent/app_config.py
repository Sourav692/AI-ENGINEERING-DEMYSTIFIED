import streamlit as st

class AppConfig:
    """Handles application configuration and styling."""
    @staticmethod
    def setup_page():
        st.set_page_config(
            page_title="AI Stock Analysis",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.markdown("""
        <style>
            .main-header {
                font-size: 3rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 2rem;
                color: #1f2a44;
                background: none;
                -webkit-background-clip: unset;
                -webkit-text-fill-color: unset;
            }
            .stButton > button {
                width: 30%;
                background: #1f2a44;
                color: white;
                border: none;
                padding: 0.75rem;
                border-radius: 0.5rem;
                font-weight: bold;
            }
            .analysis-container {
                background-color: #f8f9fa;
                padding: 1.5rem;
                border-radius: 0.5rem;
                border-left: 4px solid #1f2a44;
                margin: 1rem 0;
            }
            .metric-container {
                background: white;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 0.5rem 0;
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def initialize_session_state():
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
