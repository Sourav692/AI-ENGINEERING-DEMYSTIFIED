# ============================================================================
# LEVEL 2, Tutorial 4: Reflection and Self-Improvement Pattern
# ============================================================================
# This tutorial demonstrates a reflection pattern that combines:
# 1. Parallel generation (multiple candidates)
# 2. Selection (choose the best)
# 3. Reflection/refinement (improve the selected output iteratively)
#
# Key Concepts:
# 1. **Reflection Loop**: Iteratively refining an output by passing it back
#    as input (draft) to the same module
# 2. **Self-Improvement**: The model improves its own output over iterations
# 3. **Combined Patterns**: Merging selection (t3) with refinement (t2)
# 4. **Optional Draft Input**: Starting with None, then passing previous output
#
# Why use reflection?
# - Quality: Combines exploration (parallel) with exploitation (refinement)
# - Flexibility: Can improve any selected output, not just generate new ones
# - Progressive improvement: Each iteration builds on the previous
# - Best of both worlds: Diversity (parallel) + Quality (refinement)
#
# Pattern Flow:
# Generate N candidates (parallel) → Select best → Reflect/Refine (N times) → Output
#
# This combines patterns from:
# - t3-multi_out_refine.py: Parallel generation and selection
# - t2_iterative_refinement.py: Iterative improvement with feedback
# ============================================================================

import time
import dspy
import asyncio

from print_utils import print
from typing import List, Optional
from pydantic import BaseModel, Field

# Optional: Uncomment this to use MLflow for experiment tracking
# import mlflow
# mlflow.autolog()
# mlflow.set_tracking_uri("http://127.0.0.1:5000")
# mlflow.set_experiment("Reflection")


# Configure the language model
# Higher temperature (1.0) = more diverse/creative outputs for ideation
dspy.configure(lm=dspy.LM("openai/gpt-4.1-mini"), temperature=1)

# Disable caching for diverse generation
dspy.configure_cache(
    enable_disk_cache=False,
    enable_memory_cache=False,
)


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
    Generate or refine a joke based on the idea and optional draft.
    
    Note: This signature accepts an OPTIONAL joke_draft input.
    - First call: joke_draft=None → generates a new joke
    - Subsequent calls: joke_draft=previous_joke → refines the draft
    
    You are a funny comedian who likes to tell stories before delivering a punchline.
    You are always funny and act on the input joke idea.
    If you are provided a draft of a joke, your goal should be to make it funnier and more punchy.
    """
    joke_idea: JokeIdea = dspy.InputField()
    joke_draft: Optional[str] = dspy.InputField(
        description="An existing joke that you need to either refine, or change"
    )
    joke: str = dspy.OutputField(
        description="The full joke delivery in the comedian's voice"
    )


class JokeJudge(dspy.Signature):
    """
    Evaluate and rank multiple joke ideas.
    
    Rank each joke idea between 1-N.
    Rank 1 is the most unique and funniest.
    """
    joke_idea: List[JokeIdea] = dspy.InputField()
    joke_ratings: List[int] = dspy.OutputField(description="Rank between 1, 2, 3 ... N")


# ============================================================================
# Reward Function: Validates Ranking Quality
# ============================================================================

def check_score_goodness(args, pred):
    """
    Reward function that validates the ranking output.
    
    A valid ranking must:
    1. Have the same length as the input (one rank per joke idea)
    2. Contain all ranks from 1 to N exactly once (no duplicates, no gaps)
    
    Args:
        args: The input arguments (contains "joke_idea")
        pred: The prediction/output from the judge
    
    Returns:
        1 if the ranking is valid, 0 otherwise
    """
    num_samples = len(args["joke_idea"])
    same_length = len(pred.joke_ratings) == num_samples
    
    # Check that all ranks 1..N are present (no duplicates, no gaps)
    all_ranks_present = all([(i + 1) in pred.joke_ratings for i in range(num_samples)])
    
    return 1 if (same_length and all_ranks_present) else 0


# ============================================================================
# Reflection Module: Selection + Refinement
# ============================================================================

class ConditionalJokeGenerator(dspy.Module):
    """
    A joke generator that combines parallel generation, selection, and reflection.
    
    Process:
    1. Generate multiple joke ideas in parallel (exploration)
    2. Judge and rank all ideas
    3. Select the best-ranked idea
    4. Expand the idea into a joke (first draft)
    5. Reflect/refine the joke iteratively (exploitation)
       - Each iteration passes the previous joke as a draft
       - The model refines/improves the draft
    
    This pattern combines:
    - Parallel generation (t3): For diversity and exploration
    - Selection (t3): For choosing the best starting point
    - Reflection (t2): For iterative improvement of the selected output
    
    Key Insight: Reflection allows the model to improve its own output
    by treating the previous output as a draft to refine.
    """
    
    def __init__(self, num_samples=2, num_reflection_steps=2):
        """
        Initialize the components.
        
        Args:
            num_samples: Number of parallel candidates to generate
            num_reflection_steps: Number of reflection/refinement iterations
        """
        # ChainOfThought adds reasoning steps for better quality
        self.query_to_idea = dspy.ChainOfThought(QueryToIdea)
        self.idea_to_joke = dspy.ChainOfThought(IdeaToJoke)
        
        # Use a different LM for joke generation (potentially better quality)
        # Lower temperature (0.7) = more focused outputs for refinement
        self.idea_to_joke.set_lm(lm=dspy.LM("openai/gpt-4.1", temperature=0.7))
        
        # dspy.Refine ensures valid rankings
        self.judge = dspy.Refine(
            module=dspy.ChainOfThought(JokeJudge),
            N=3,
            reward_fn=check_score_goodness,
            threshold=1,
        )

        self.num_samples = num_samples
        self.num_reflection_steps = num_reflection_steps

    async def aforward(self, query: str):
        """
        Execute the reflection pipeline.
        
        Args:
            query: User's request for a joke
            
        Returns:
            The final refined joke
        """
        # Step 1: Generate multiple candidates in parallel (exploration)
        joke_ideas = await asyncio.gather(
            *[self.query_to_idea.acall(query=query) for _ in range(self.num_samples)]
        )

        print("Generated Joke Ideas: \n", joke_ideas)

        # Step 2: Judge and rank all candidates
        judge_score = self.judge(joke_idea=joke_ideas).joke_ratings
        print("Judge Score for each: ", judge_score)

        # Step 3: Select the best-ranked idea
        best_joke_idea_idx = judge_score.index(1)
        selected_joke_idea = joke_ideas[best_joke_idea_idx]
        print("Selected Joke Idea: \n", selected_joke_idea)
        
        # Step 4: Reflection loop - iteratively refine the joke
        # Start with no draft (None), then pass previous output as draft
        joke = None  # No draft on first iteration
        
        for iteration in range(self.num_reflection_steps):
            # Generate or refine the joke
            # Iteration 1: joke_draft=None → generates new joke
            # Iteration 2+: joke_draft=previous_joke → refines the draft
            joke = self.idea_to_joke(
                joke_idea=selected_joke_idea,
                joke_draft=joke.joke if joke else None  # Pass previous joke as draft
            )
            print(f"iteration: {iteration + 1}: Joke: {joke}")
        
        return joke


# ============================================================================
# Execution: Async Main Function
# ============================================================================

async def main():
    """
    Main execution function for async code.
    
    Includes timing to measure execution time.
    """
    joke_generator = ConditionalJokeGenerator()
    
    start_time = time.time()
    joke = await joke_generator.acall(
        query="Write a joke about AI that has to do with them turning rogue."
    )

    print("---")
    print(joke)
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
