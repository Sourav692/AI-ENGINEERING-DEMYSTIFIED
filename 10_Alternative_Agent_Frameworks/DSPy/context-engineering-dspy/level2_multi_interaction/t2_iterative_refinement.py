# ============================================================================
# LEVEL 2, Tutorial 2: Iterative Refinement Pattern
# ============================================================================
# This tutorial demonstrates an iterative improvement pattern where we:
# 1. Generate an initial output
# 2. Evaluate it (get feedback)
# 3. Refine based on feedback
# 4. Repeat until satisfied or max iterations reached
#
# Key Concepts:
# 1. **Feedback Loop**: Using one LLM call to critique another's output
# 2. **Optional Inputs**: Passing context (draft, feedback) that may be None initially
# 3. **ChainOfThought**: Using reasoning chains for more thoughtful evaluations
# 4. **Iterative Improvement**: Each iteration builds on the previous attempt
#
# Why use iterative refinement?
# - Higher quality outputs: Each iteration improves on the previous
# - Self-correction: The system can identify and fix its own mistakes
# - Adaptive: Responds to feedback dynamically
# - Transparent: You can see how the output evolves
#
# Pattern Flow:
# Generate → Evaluate → Refine → Generate (with context) → Evaluate → ...
# ============================================================================

import dspy
from print_utils import print
from typing import Optional
from pydantic import BaseModel, Field

# Configure the language model
dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))


class JokeIdea(BaseModel):
    """Structured representation of a joke concept."""
    setup: str
    contradiction: str
    punchline: str


# ============================================================================
# Signatures for the Pipeline
# ============================================================================

class QueryToIdea(dspy.Signature):
    """
    Convert user query into a structured joke idea.
    
    You are a funny comedian and your goal is to generate a nice structure for a joke.
    """
    query: str = dspy.InputField()
    joke_idea: JokeIdea = dspy.OutputField()


class IdeaToJoke(dspy.Signature):
    """
    Generate or refine a joke based on the idea and optional feedback.
    
    Note: This signature accepts OPTIONAL inputs (draft_joke, feedback).
    On the first iteration, these will be None. On subsequent iterations,
    they provide context for refinement.
    
    You are a funny comedian who likes to tell stories before delivering a punchline. 
    You are always funny and act on the input joke idea.
    """
    joke_idea: JokeIdea = dspy.InputField()
    draft_joke: Optional[str] = dspy.InputField(description="a draft joke")
    feedback: Optional[str] = dspy.InputField(description="feedback on the draft joke")
    joke: str = dspy.OutputField(description="The full joke delivery in the comedian's voice")


class Refinement(dspy.Signature):
    """
    Evaluate a joke and provide feedback for improvement.
    
    This is the "critic" component that assesses quality and suggests changes.
    
    Given a joke, is it funny? If not, suggest a change.
    """
    joke_idea: JokeIdea = dspy.InputField()
    joke: str = dspy.InputField()
    feedback: str = dspy.OutputField()


# ============================================================================
# Iterative Refinement Module
# ============================================================================

class IterativeJokeGenerator(dspy.Module):
    """
    A joke generator that improves its output through iterative refinement.
    
    The refinement loop:
    1. Generate a joke (or refine based on previous draft + feedback)
    2. Get evaluation/feedback on the joke
    3. Use feedback to refine in the next iteration
    4. Repeat for n_attempts iterations
    
    Note: Using ChainOfThought for the refinement step helps the model
    reason about what makes a joke good before providing feedback.
    """
    
    def __init__(self, n_attempts: int = 3):
        """
        Initialize the components.
        
        Args:
            n_attempts: Number of refinement iterations to perform
        """
        self.query_to_idea = dspy.Predict(QueryToIdea)
        self.idea_to_joke = dspy.Predict(IdeaToJoke)
        
        # ChainOfThought adds reasoning steps, making evaluations more thoughtful
        self.refinement = dspy.ChainOfThought(Refinement)
        
        self.n_attempts = n_attempts

    def forward(self, query: str):
        """
        Execute the iterative refinement pipeline.
        
        Args:
            query: User's request for a joke
            
        Returns:
            The final refined joke
        """
        # Step 1: Generate the initial joke idea (once)
        joke_idea = self.query_to_idea(query=query)
        print(f"Joke Idea:\n{joke_idea}")
        
        # Initialize state for the refinement loop
        draft_joke = None      # No draft on first iteration
        feedback = None        # No feedback on first iteration

        # Iterative refinement loop
        for iteration in range(self.n_attempts):
            print(f"--- Iteration {iteration + 1} ---")

            # Generate/refine the joke
            # On iteration 1: draft_joke=None, feedback=None → generates new joke
            # On iteration 2+: draft_joke and feedback provide context → refines
            joke = self.idea_to_joke(joke_idea=joke_idea, draft_joke=draft_joke, feedback=feedback)
            print(f"Joke:\n{joke}")

            # Evaluate the joke and get feedback
            feedback_result = self.refinement(joke_idea=joke_idea, joke=joke)
            print(f"Feedback:\n{feedback_result}")

            # Update state for next iteration
            draft_joke = joke.joke                    # Save current joke as draft
            feedback = feedback_result.feedback       # Save feedback for next iteration

        return joke


# ============================================================================
# Execution
# ============================================================================

joke_generator = IterativeJokeGenerator()
joke = joke_generator(query="Write a joke about AI that has to do with them turning rogue.")

print("---")
print(joke.joke)
