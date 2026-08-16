# ============================================================================
# LEVEL 2, Tutorial 1: Sequential Multi-Step Pipeline
# ============================================================================
# This tutorial demonstrates the simplest multi-step interaction pattern in DSPy:
# a sequential pipeline where each step's output becomes the next step's input.
#
# Key Concepts:
# 1. **Modular Design**: Breaking complex tasks into smaller, focused steps
# 2. **dspy.Module**: Custom classes that compose multiple DSPy components
# 3. **Sequential Flow**: Step 1 → Step 2 → Result
# 4. **Structured Data**: Using Pydantic models for type-safe outputs
#
# Why use multi-step pipelines?
# - Separation of concerns: Each step has a clear, focused responsibility
# - Easier debugging: You can inspect intermediate results
# - Better quality: Each step can be optimized independently
# - Reusability: Steps can be reused in different combinations
#
# In this example:
# Step 1: Convert user query → structured joke idea (setup, contradiction, punchline)
# Step 2: Convert joke idea → full joke delivery
# ============================================================================

import dspy
from print_utils import print
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

# Configure the language model for all DSPy operations
dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

# ============================================================================
# Data Models: Structured Outputs
# ============================================================================
# Pydantic models define the structure of our intermediate data.
# This provides type safety and validation, ensuring the LLM outputs
# match our expected format.

class JokeIdea(BaseModel):
    """Structured representation of a joke concept before full development."""
    setup: str              # The initial premise or scenario
    contradiction: str      # The twist or unexpected element
    punchline: str          # The humorous resolution


# ============================================================================
# DSPy Signatures: Define Input-Output Contracts
# ============================================================================
# Signatures define WHAT each step should do (the contract).
# The docstring becomes part of the system prompt, guiding the LLM's behavior.

class QueryToIdea(dspy.Signature):
    """
    First step: Convert a user's query into a structured joke idea.
    
    You are a funny comedian and your goal is to generate a nice structure for a joke.
    """
    query: str = dspy.InputField()                    # User's request (e.g., "joke about AI")
    joke_idea: JokeIdea = dspy.OutputField()          # Structured output: setup, contradiction, punchline


class IdeaToJoke(dspy.Signature):
    """
    Second step: Expand the structured idea into a full joke delivery.
    
    You are a funny comedian who likes to tell stories before delivering a punchline. 
    You are always funny and act on the input joke idea.
    """
    joke_idea: JokeIdea = dspy.InputField()           # Input from previous step
    joke: str = dspy.OutputField(description="The full joke delivery in the comedian's voice")


# ============================================================================
# DSPy Module: Composing Multiple Steps
# ============================================================================
# A dspy.Module is a custom class that combines multiple DSPy components.
# It's the building block for creating complex, reusable pipelines.

class JokeGenerator(dspy.Module):
    """
    A complete joke generation pipeline composed of two sequential steps.
    
    Architecture:
    - __init__: Defines the components (predictors) we'll use
    - forward: Defines the execution flow (how components interact)
    """
    
    def __init__(self):
        # Initialize our predictor modules
        # dspy.Predict converts a Signature into an executable module
        self.query_to_idea = dspy.Predict(QueryToIdea)
        self.idea_to_joke = dspy.Predict(IdeaToJoke)

    def forward(self, query: str):
        """
        Execute the sequential pipeline:
        1. Generate a structured joke idea from the query
        2. Expand the idea into a full joke
        
        Args:
            query: User's request for a joke
            
        Returns:
            The final joke output
        """
        # Step 1: Query → Structured Idea
        # The output is a structured JokeIdea object (not raw text)
        joke_idea = self.query_to_idea(query=query)
        print(f"Joke Idea:\n{joke_idea}")

        # Step 2: Structured Idea → Full Joke
        # Pass the structured object from step 1 as input to step 2
        joke = self.idea_to_joke(joke_idea=joke_idea)
        print(f"Joke:\n{joke}")
        return joke


# ============================================================================
# Execution: Using the Pipeline
# ============================================================================
# Create an instance of our module and use it like a function.
# DSPy handles all the prompt construction, API calls, and parsing automatically.

joke_generator = JokeGenerator()
joke = joke_generator(query="Write a joke about AI that has to do with them turning rogue.")

print("---")
print(joke.joke)
