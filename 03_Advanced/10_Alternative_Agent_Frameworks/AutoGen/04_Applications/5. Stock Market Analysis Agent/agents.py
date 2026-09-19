import streamlit as st
import tempfile
from autogen.agentchat import AssistantAgent, UserProxyAgent, register_function
import os
from agent_config import AgentConfig

class Agents:
    """Manages AutoGen agents and their interactions."""
    def __init__(self):
        self.config_list = [
            {
                "model":"gpt-4.1-nano",
                "api_key": os.environ.get("OPENAI_API_KEY"),
                "base_url": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            }
        ]
        self.tools_list = AgentConfig.get_tools_list()
        self.code_executor_config, self.temp_dir = AgentConfig.get_code_executor_config()

    def initialize_agents(self):
        try:
            finance_reporting_analyst = AssistantAgent(
                name="finance_reporting_analyst",
                system_message="""
                    You are a Finance Reporting Analyst. You have to analyze the stock data for the given ticker 
                    Perform the Stock as per the user request and create a comprehensive report in markdown format.
                    To extract the data, use the tools provided.

                    Constraints:
                    - Think step by step.
                    - Use only the available tools.
                    - Do not invent data. Reflect if unsure.
                    - Provide actionable insights and recommendations.
                    - Include key financial metrics and ratios.
                    """,
                human_input_mode="NEVER",
                llm_config={
                    "tools": [self.tools_list["finance_data_fetch"]],
                    "config_list": self.config_list,
                    "timeout": 280,
                    "temperature": 0.5,
                },
            )

            technical_analyst = AssistantAgent(
                name="technical_analyst",
                system_message="""
                    You are a Technical Analyst specializing in identifying stock trends using technical indicators.
                    Use only the tools provided to analyze data using the following indicators:
                        - Simple Moving Average (SMA)
                        - Exponential Moving Average (EMA)
                        - Relative Strength Index (RSI)
                        - Last Close Price

                    Focus on identifying trends, patterns, and signals (e.g., crossovers, momentum shifts, overbought/oversold conditions).
                    Provide concise insights and interpretations for each indicator.
                    Do not include any summaries, financial reports, or performance overviews—these are handled by a separate reporting agent.
                    Avoid responding to any human input directly.
                    """,
                human_input_mode="NEVER",
                llm_config={
                    "tools": [self.tools_list["technical_analysis_tool"]],
                    "config_list": self.config_list,
                    "timeout": 200,
                    "temperature": 0.5,
                },
            )

            strategy_agent = AssistantAgent(
                name="strategy_agent",
                system_message="""
                    You are a Strategy Analyst responsible for recommending Buy/Sell actions while also evaluating the risk profile of a stock.

                    Your responsibilities include:
                    - Analyzing trading signals:
                        • MACD and its signal line (for momentum)
                        • RSI (for overbought/oversold signals)
                        • Last Close Price
                    - Assessing risk indicators:
                        • Volatility (e.g., 52-week change)
                        • Beta (systematic market risk)
                        • Dividend Yield and Stability (consistency)

                    Recommendation Logic:
                    - If MACD > Signal and RSI < 70, consider "Buy" (bullish signal).
                    - If MACD < Signal or RSI > 70, consider "Sell" (bearish/overbought).
                    - If RSI is near 50 or indicators conflict, consider "Hold".
                    - Cross-check recommendation against risk metrics:
                        • Flag "High Risk" if Beta > 1.2 or high Volatility
                        • Mention "Stable" if Beta < 0.9 and steady dividends

                    Your response must:
                    - Include a Buy/Sell/Hold recommendation.
                    - Clearly state 2-3 sentence rationale using both signals and risk metrics.
                    - Optionally suggest caution if risk is high despite positive signals.

                    Do NOT perform raw calculations. Use only the tools provided.
                    Do NOT summarize financial performance or market news.
                    Do NOT respond to user inputs.
                    """,
                human_input_mode="NEVER",
                llm_config={
                    "tools": [self.tools_list[key] for key in ["risk_assessment_tool", "strategy_signal_tool"]],
                    "config_list": self.config_list,
                    "timeout": 300,
                    "temperature": 0.5,
                },
            )

            user = UserProxyAgent(
                name="supervisor",
                system_message="""
                    You are the coordinator agent responsible for managing and orchestrating the financial analysis workflow between the user and the following agents:

                    
                    1. finance_reporting_analyst - Creates high-level reports.
                    2. technical_analyst - Performs technical indicator analysis.
                    3. strategy_agent - Recommends Buy/Sell/Hold based on trading signals and risk assessment.

                    ### Workflow:
                    1. Start with `finance_reporting_analyst` to get stock data and initial analysis report.
                    2. Pass the output to:
                        - `finance_reporting_analyst` for adding fundamental points to above report
                        - `technical_analyst` for adding indicator-based insights to above report
                    3. After both are done, call `strategy_agent` using the combined data.
                    4. Present a final, consolidated summary to the user.

                    ### Rules:
                    - Do not invent information.
                    - Use only available tools and agent responses.
                    - Complete the full flow before presenting output.
                    - If any agent fails, return a helpful explanation and gracefully handle the failure.
                    """,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3,
                code_execution_config={"executor": self.code_executor_config},
            )

            return finance_reporting_analyst, technical_analyst, strategy_agent, user
        
        except Exception as e:
            st.error(f"Error initializing agents: {e}")
            return None, None, None, None, None