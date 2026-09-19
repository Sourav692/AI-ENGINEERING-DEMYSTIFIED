# ============================================================================
# LEVEL 2, Tutorial 3 (Refined): Parallel Generation with dspy.Refine
# ============================================================================
# This tutorial extends the parallel generation pattern by using dspy.Refine
# to automatically improve the judge's ranking output.
#
# Key Concepts:
# 1. **dspy.Refine**: A module wrapper that iteratively improves outputs
# 2. **Reward Function**: A function that scores the quality of outputs
# 3. **Threshold**: The minimum quality score to accept (stops refinement)
# 4. **Per-Module LM Configuration**: Different LMs for different steps
#
# Why use dspy.Refine?
# - Reliability: Ensures outputs meet quality criteria (e.g., valid rankings)
# - Self-correction: Automatically fixes malformed outputs
# - Quality guarantee: Only accepts outputs that pass the reward function
# - Robustness: Handles edge cases (e.g., duplicate rankings, missing ranks)
#
# Pattern Flow:
# Generate N candidates → Judge with Refine (retry if invalid) → Select best → Refine
#
# Compare to t3-multi_out.py:
# - t3-multi_out.py: Simple ranking (may produce invalid rankings)
# - t3-multi_out_refine.py: Guaranteed valid rankings via Refine
# ============================================================================

import dspy
import asyncio
from print_utils import print
from typing import List
from pydantic import BaseModel, Field

# Configure the language model
# Higher temperature (1.0) = more diverse/creative outputs
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
    Expand a structured idea into a full joke delivery.
    
    You are a funny comedian who likes to tell stories before delivering a punchline.
    You are always funny and act on the input joke idea.
    """
    joke_idea: JokeIdea = dspy.InputField()
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
    all_ranks_present = all([(i+1) in pred.joke_ratings for i in range(num_samples)])
    
    return 1 if (same_length and all_ranks_present) else 0


# ============================================================================
# Parallel Generation with Refined Selection Module
# ============================================================================

class ConditionalJokeGenerator(dspy.Module):
    """
    A joke generator using parallel generation with refined selection.
    
    This module uses dspy.Refine to ensure the judge produces valid rankings.
    If the judge outputs an invalid ranking (e.g., duplicates, missing ranks),
    Refine will retry up to N times until it gets a valid ranking.
    
    Key improvements over t3-multi_out.py:
    - Uses ChainOfThought for better reasoning
    - Uses dspy.Refine for guaranteed valid rankings
    - Uses different LMs for different steps (optimize cost/quality)
    """
    
    def __init__(self, num_samples=3):
        """
        Initialize the components.
        
        Args:
            num_samples: Number of parallel candidates to generate
        """
        # ChainOfThought adds reasoning steps for better quality
        self.query_to_idea = dspy.ChainOfThought(QueryToIdea)
        self.idea_to_joke = dspy.ChainOfThought(IdeaToJoke)
        
        # Use a different (potentially better) LM for the final joke generation
        # This allows you to use a faster/cheaper model for ideation and
        # a better model only for the final output
        self.idea_to_joke.set_lm(lm=dspy.LM("openai/gpt-4.1", temperature=0.7))
        
        # dspy.Refine wraps the judge to ensure valid outputs
        # - N=3: Retry up to 3 times if the output is invalid
        # - reward_fn: Function that scores output quality (1 = good, 0 = bad)
        # - threshold=1: Only accept outputs with score 1 (perfect)
        self.judge = dspy.Refine(
            module=dspy.ChainOfThought(JokeJudge),
            N=3,
            reward_fn=check_score_goodness,
            threshold=1,
        )

        self.num_samples = num_samples

    async def aforward(self, query: str):
        """
        Execute the parallel generation and refined selection pipeline.
        
        Args:
            query: User's request for a joke
            
        Returns:
            The final joke based on the best-ranked idea
        """
        # Step 1: Generate multiple candidates in parallel
        joke_ideas = await asyncio.gather(
            *[self.query_to_idea.acall(query=query) for _ in range(self.num_samples)]
        )

        print("Generated Joke Ideas: \n", joke_ideas)

        # Step 2: Judge and rank (with Refine ensuring valid rankings)
        # Refine will retry if check_score_goodness returns 0
        judge_score = self.judge(joke_idea=joke_ideas).joke_ratings
        print("Judge Score for each: ", judge_score)

        # Step 3: Select the best-ranked idea (rank 1)
        best_joke_idea_idx = judge_score.index(1)

        print("Selected Index: ", best_joke_idea_idx)
        selected_joke_idea = joke_ideas[best_joke_idea_idx]
        print("Selected Joke Idea: \n", selected_joke_idea)

        # Step 4: Expand the selected idea into a full joke
        # Uses the LM configured via set_lm() (potentially different from default)
        joke = self.idea_to_joke(joke_idea=selected_joke_idea)

        # Optional: Use a different LLM for the final expansion
        # with dspy.context(lm=dspy.LM("gemini/gemini-1.5-pro")):
        #    joke = self.idea_to_joke(joke_idea=selected_joke_idea)

        return joke


# ============================================================================
# Execution: Async Main Function
# ============================================================================

async def main():
    """Main execution function for async code."""
    joke_generator = ConditionalJokeGenerator()
    joke = await joke_generator.acall(
        query="Write a joke about AI that has to do with them turning rogue."
    )

    print("---")
    print(joke)


if __name__ == "__main__":
    asyncio.run(main())
