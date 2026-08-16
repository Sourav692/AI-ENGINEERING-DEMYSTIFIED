"""
LLM Utility Functions for LangGraph Applications
=================================================

This module provides helper functions to create and configure Large Language Model (LLM) 
instances from different providers (OpenAI and Groq). These utilities are used throughout 
the LangGraph tutorials to maintain consistent LLM initialization.

Why use utility functions for LLM initialization?
-------------------------------------------------
1. **Centralized Configuration**: All LLM settings are managed in one place
2. **Easy Provider Switching**: Switch between OpenAI and Groq with a single function call
3. **Default Parameters**: Sensible defaults (like temperature=0 for deterministic outputs)
4. **Code Reusability**: Avoid repeating initialization code across notebooks

Dependencies:
- langchain_groq: LangChain integration for Groq's fast inference API
- langchain.chat_models: LangChain's chat model abstractions for OpenAI
- python-dotenv: For loading API keys from .env files
"""

# ============================================================================
# IMPORTS
# ============================================================================

# ChatGroq: LangChain wrapper for Groq's API - known for extremely fast inference
from langchain_groq import ChatGroq

# ChatOpenAI: LangChain wrapper for OpenAI's Chat API (GPT-3.5, GPT-4, etc.)
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from databricks_langchain import ChatDatabricks
from langchain_groq import ChatGroq

# python-dotenv: Loads environment variables from a .env file
# This keeps API keys secure and out of source code
from dotenv import load_dotenv

# os module: Used to access environment variables after they're loaded
import os

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

# Load environment variables from .env file in the project root
# Your .env file should contain:
#   OPENAI_API_KEY=your_openai_api_key_here
#   GROQ_API_KEY=your_groq_api_key_here
# 
# SECURITY NOTE: Never commit .env files to version control!
load_dotenv()


# ============================================================================
# LLM FACTORY FUNCTIONS
# ============================================================================

def get_openai_llm(model_name: str = "gpt-4o-mini", temperature: float = 0):
    """
    Create and return an OpenAI Chat LLM instance.
    
    This function creates a ChatOpenAI instance configured for use with LangGraph.
    OpenAI models are known for their strong reasoning and instruction-following capabilities.
    
    Parameters:
    -----------
    model_name : str, default="gpt-4o-mini"
        The OpenAI model to use. Common options:
        - "gpt-4o-mini": Fast, cost-effective, good for most tasks (recommended for learning)
        - "gpt-4o": Most capable model, best for complex reasoning
        - "gpt-4-turbo": Balance of capability and speed
        - "gpt-3.5-turbo": Fastest and cheapest, good for simple tasks
    
    temperature : float, default=0
        Controls randomness in responses (0.0 to 2.0):
        - 0: Deterministic, consistent outputs (best for agents & tools)
        - 0.7: Balanced creativity and consistency
        - 1.0+: More creative/random outputs
    
    Returns:
    --------
    ChatOpenAI
        A configured LangChain ChatOpenAI instance ready for use in chains/agents
    
    Example:
    --------
    >>> llm = get_openai_llm()  # Uses defaults
    >>> llm = get_openai_llm(model_name="gpt-4o", temperature=0.5)
    >>> response = llm.invoke("Hello, world!")
    
    Note:
    -----
    Requires OPENAI_API_KEY environment variable to be set.
    """
    return ChatOpenAI(
        model=model_name,
        temperature=temperature
    )


def get_groq_llm(model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
    """
    Create and return a Groq Chat LLM instance.
    
    Groq provides extremely fast inference using their custom LPU (Language Processing Unit)
    hardware. This makes it excellent for applications requiring low latency responses.
    
    Parameters:
    -----------
    model_name : str, default="llama-3.3-70b-versatile"
        The model to use via Groq's API. Popular options:
        - "llama-3.3-70b-versatile": Latest Llama 3.3, great balance of speed & quality
        - "llama-3.1-70b-versatile": Llama 3.1 70B, excellent for complex tasks
        - "llama-3.1-8b-instant": Smaller, faster model for simpler tasks
        - "mixtral-8x7b-32768": Mixtral model with 32k context window
        - "gemma2-9b-it": Google's Gemma 2 model
    
    temperature : float, default=0
        Controls randomness in responses (0.0 to 2.0):
        - 0: Deterministic outputs (recommended for agents & tool use)
        - Higher values: More creative/varied responses
    
    Returns:
    --------
    ChatGroq
        A configured LangChain ChatGroq instance ready for use in chains/agents
    
    Example:
    --------
    >>> llm = get_groq_llm()  # Uses defaults
    >>> llm = get_groq_llm(model_name="llama-3.1-8b-instant", temperature=0.3)
    >>> response = llm.invoke("Explain quantum computing")
    
    Why use Groq?
    -------------
    - Extremely fast inference (often 10x faster than traditional cloud providers)
    - Cost-effective for high-volume applications
    - Supports popular open-source models (Llama, Mixtral, etc.)
    
    Note:
    -----
    Requires GROQ_API_KEY environment variable to be set.
    Get your free API key at: https://console.groq.com/

    ## Use openai/gpt-oss-120b if you want to use OpenAI's models
    ## Use moonshotai/kimi-k2-instruct-0905 if you want to use Moonshot's models
    """
    return ChatGroq(
        model=model_name,
        temperature=temperature
    )


def get_databricks_llm(model_name: str = "databricks-gpt-5-2", temperature: float = 0.1):
    """
    Create and return a Databricks Chat LLM instance.
    """
    return ChatDatabricks(
        endpoint=model_name,
        temperature=temperature
    )