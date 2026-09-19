import os
import tempfile
from autogen.coding import LocalCommandLineCodeExecutor

class AgentConfig:
    """Configuration settings for the AutoGen application."""
    
    @staticmethod
    def get_llm_config():
        return [
            {
                "model": "gpt-4.1-nano",
                "api_key": os.environ.get("OPENAI_API_KEY"),
                "base_url": os.environ.get("OPENAI_BASE_URL"),
            }
        ]
    
    @staticmethod
    def get_tools_list():
        return {
            "finance_data_fetch": {
                "type": "function",
                "function": {
                    "name": "finance_data_fetch",
                    "description": "Fetch recent stock information for a ticker symbol",
                    "parameters": {
                        "type": "object",
                        "properties": {"ticker": {"type": "string"}},
                        "required": ["ticker"],
                    },
                },
            },
            "technical_analysis_tool": {
                "type": "function",
                "function": {
                    "name": "technical_analysis_tool",
                    "description": "Perform technical analysis using moving averages and RSI",
                    "parameters": {
                        "type": "object",
                        "properties": {"ticker": {"type": "string"}},
                        "required": ["ticker"],
                    },
                },
            },
            "risk_assessment_tool": {
                "type": "function",
                "function": {
                    "name": "risk_assessment_tool",
                    "description": "Perform risk evaluation using beta, volatility, and dividend yield",
                    "parameters": {
                        "type": "object",
                        "properties": {"ticker": {"type": "string"}},
                        "required": ["ticker"],
                    },
                },
            },
            "strategy_signal_tool": {
                "type": "function",
                "function": {
                    "name": "strategy_signal_tool",
                    "description": "Evaluate trading signals using MACD, RSI, and closing price",
                    "parameters": {
                        "type": "object",
                        "properties": {"ticker": {"type": "string"}},
                        "required": ["ticker"],
                    },
                },
            },
        }
    
    @staticmethod
    def get_code_executor_config():
        temp_dir = tempfile.TemporaryDirectory()
        return LocalCommandLineCodeExecutor(
            timeout=30,
            work_dir=temp_dir.name,
        ), temp_dir