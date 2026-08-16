import streamlit as st
import os
from datetime import datetime
from openai import OpenAI
import uuid
from agents import Agents
from agent_orchestrator import orchestrate_agents
from app_config import AppConfig
from tools import FinanceTools

class OpenAIClient:
    """Manages OpenAI client initialization."""
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("OPENAI_BASE_URL")
        )

class StockAnalysisApp:
    """Main application class for the AI Stock Analysis Platform."""
    def __init__(self):
        self.config = AppConfig()
        self.openai_client = OpenAIClient()
        self.agents = Agents()

    def render_sidebar(self):
        with st.sidebar:
            st.header("🔧 Configuration")
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.environ.get("OPENAI_API_KEY", ""),
                help="Enter your OpenAI API key"
            )
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key

            st.divider()
            st.header("📊 Quick Stock Info")
            quick_ticker = st.text_input("Enter ticker for quick view:", placeholder="e.g., AAPL")
            if quick_ticker:
                quick_ticker = quick_ticker.upper()
                metrics = FinanceTools.get_stock_metrics(quick_ticker)
                for metric, value in metrics.items():
                    st.metric(metric, value)

    def render_main_content(self):
        st.markdown('<h1 class="main-header">📈 AI Stock Analysis Platform</h1>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;"><strong>Powered by AutoGen AI Agents</strong></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            user_request = st.text_input(
                "Enter your query:",
                placeholder="Should I invest in MSFT based on recent trends?",
                help="Mention stock symbol you want to analyze"
            )

        if st.button("Run Analysis", disabled=not(user_request)):
            if not os.environ.get("OPENAI_API_KEY"):
                st.error("⚠️ Please provide your OpenAI API key in the sidebar")
            else:
                with st.spinner("🤖 AI agents are analyzing the stock... This may take a few moments."):
                    agents = self.agents.initialize_agents()
                    if all(agents):
                        analysis_data = orchestrate_agents(user_request, *agents)
                        st.session_state.analysis_results[user_request] = {
                            "timestamp": datetime.now(),
                            "request": user_request,
                            "result": analysis_data
                        }
                        st.session_state.chat_history.append({
                            "timestamp": datetime.now(),
                            "ticker": user_request,
                            "request": user_request,
                            "result": analysis_data
                        })

        if user_request in st.session_state.analysis_results:
            st.header("📋 Analysis Results")
            st.markdown(st.session_state.analysis_results[user_request]["result"], unsafe_allow_html=True)
            file_id = uuid.uuid1()
            st.download_button(
                label="📥 Download Analysis Report",
                data=st.session_state.analysis_results[user_request]["result"],
                file_name=f"{file_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )

        st.markdown("---")
        st.markdown(
            "**Disclaimer:** This analysis is for educational purposes only. "
            "Always consult with a financial advisor before making investment decisions."
        )

    def run(self):
        self.config.setup_page()
        self.config.initialize_session_state()
        self.render_sidebar()
        self.render_main_content()

if __name__ == "__main__":
    app = StockAnalysisApp()
    app.run()