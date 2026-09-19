# ============================================================================
# LEVEL 2, Tutorial 3 (Conditional): Conditional Branching with Threshold
# ============================================================================
# This tutorial demonstrates conditional branching based on quality thresholds.
# Instead of generating multiple candidates and selecting one, we:
# 1. Generate a candidate
# 2. Evaluate it
# 3. If it meets the threshold, accept it
# 4. If not, try again (up to max_attempts)
#
# Key Concepts:
# 1. **Conditional Logic**: Using if/break to control flow based on quality
# 2. **Threshold-based Selection**: Accept outputs that meet a quality bar
# 3. **Early Termination**: Stop generating once we find a good output
# 4. **Numeric Constraints**: Using Pydantic constraints (le, ge) for validation
#
# Why use conditional branching?
# - Efficiency: Stop once you find a good output (don't generate unnecessarily)
# - Quality guarantee: Only proceed with outputs that meet your standards
# - Cost control: Limit the number of attempts
# - Adaptive: Different queries may need different numbers of attempts
#
# Pattern Flow:
# Generate → Evaluate → If good: proceed | If bad: retry (up to max_attempts)
#
# Compare to other patterns:
# - t3-multi_out.py: Generate all, then select (good for comparison)
# - t3_conditional_branch.py: Generate until good (good for efficiency)
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
# DSPy Signatures
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
    Expand a structured idea into a full joke delivery.
    
    You are a funny comedian who likes to tell stories before delivering a punchline. 
    You are always funny and act on the input joke idea.
    """
    joke_idea: JokeIdea = dspy.InputField()
    joke: str = dspy.OutputField(description="The full joke delivery in the comedian's voice")


class JokeJudge(dspy.Signature):
    """
    Evaluate a single joke idea and provide a numeric rating.
    
    Note: This evaluates ONE idea (unlike JokeJudge in t3-multi_out.py
    which evaluates multiple ideas and ranks them).
    
    Is this joke idea funny?
    """
    joke_idea: JokeIdea = dspy.InputField()
    
    # Pydantic constraints ensure the rating is between 1 and 5
    # le = less than or equal, ge = greater than or equal
    joke_rating: int = dspy.OutputField(
        description="Rating between 1 to 5",
        le=5,  # maximum value: 5
        ge=1   # minimum value: 1
    )


# ============================================================================
# Conditional Branching Module
# ============================================================================

class ConditionalJokeGenerator(dspy.Module):
    """
    A joke generator that uses conditional branching based on quality thresholds.
    
    Process:
    1. Generate a joke idea
    2. Evaluate it (get a rating 1-5)
    3. If rating >= threshold: accept and proceed to joke generation
    4. If rating < threshold: retry (up to max_attempts)
    5. Expand the accepted idea into a full joke
    
    This pattern is useful when:
    - You want to ensure quality before proceeding
    - You want to limit unnecessary generation
    - You want early termination when a good output is found
    """
    
    def __init__(self, max_attempts=3, good_idea_threshold=4):
        """
        Initialize the components.
        
        Args:
            max_attempts: Maximum number of attempts to find a good idea
            good_idea_threshold: Minimum rating (1-5) to accept an idea
        """
        self.query_to_idea = dspy.Predict(QueryToIdea)
        self.idea_to_joke = dspy.Predict(IdeaToJoke)
        
        # ChainOfThought helps the model reason about quality before rating
        self.judge = dspy.ChainOfThought(JokeJudge)
        
        self.max_attempts = max_attempts
        self.good_idea_threshold = good_idea_threshold

    def forward(self, query: str):
        """
        Execute the conditional branching pipeline.
        
        Args:
            query: User's request for a joke
            
        Returns:
            The final joke based on an accepted idea
        """
        # Try up to max_attempts times to find a good idea
        for attempt in range(self.max_attempts):
            print(f"--- Iteration {attempt + 1} ---")
            
            # Step 1: Generate a joke idea
            joke_idea = self.query_to_idea(query=query)
            print(f"Joke Idea:\n{joke_idea}")
            
            # Step 2: Evaluate the idea
            judge_score = self.judge(joke_idea=joke_idea).joke_rating
            print(f"\n\n---\nJudge score: ", judge_score)

            # Step 3: Conditional check - if good enough, accept and break
            if judge_score >= self.good_idea_threshold:
                print("Judge said it was awesome, breaking the loop")
                break
            # If not good enough, the loop continues (tries again)
        
        # Step 4: Expand the accepted idea (or the last attempt if none met threshold)
        # Note: joke_idea from the last iteration is used here
        joke = self.idea_to_joke(joke_idea=joke_idea)

        # Optional: Use a different LLM for the final expansion
        # with dspy.context(lm=dspy.LM("gemini/gemini-1.5-pro")):
        #    joke = self.idea_to_joke(joke_idea=joke_idea)

        return joke


# ============================================================================
# Execution
# ============================================================================

joke_generator = ConditionalJokeGenerator()
joke = joke_generator(query="Write a joke about AI that has to do with them turning rogue.")

print("---")
print(joke)
