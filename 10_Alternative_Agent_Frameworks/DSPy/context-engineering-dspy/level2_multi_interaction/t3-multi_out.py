# ============================================================================
# LEVEL 2, Tutorial 3: Parallel Generation and Selection Pattern
# ============================================================================
# This tutorial demonstrates a parallel generation and selection pattern:
# 1. Generate multiple candidate outputs in parallel (using async)
# 2. Evaluate and rank all candidates
# 3. Select the best one
# 4. Refine the selected candidate
#
# Key Concepts:
# 1. **Parallel Generation**: Using asyncio to generate multiple candidates simultaneously
# 2. **Selection/Ranking**: Using an LLM to judge and rank multiple outputs
# 3. **Async Forward**: Using aforward() and acall() for asynchronous execution
# 4. **List Inputs**: Passing multiple items to a signature for comparison
#
# Why use parallel generation?
# - Diversity: Generate multiple diverse options
# - Quality: Select the best from multiple candidates
# - Efficiency: Generate in parallel (faster than sequential)
# - Exploration: Explore the solution space more thoroughly
#
# Pattern Flow:
# Generate N candidates (parallel) → Judge/Rank all → Select best → Refine
# ============================================================================

import dspy
import asyncio
from print_utils import print
from typing import List
from pydantic import BaseModel, Field

# Configure the language model
dspy.configure(lm=dspy.LM("openai/gpt-4.1-mini"))

# Disable caching to ensure fresh generation for each candidate
# (In production, you might want caching, but for generating diverse
#  candidates, fresh outputs are often better)
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
    joke: str = dspy.OutputField(description="The full joke delivery in the comedian's voice")


class JokeJudge(dspy.Signature):
    """
    Evaluate and rank multiple joke ideas.
    
    Note: This signature takes a LIST of joke ideas and outputs a LIST of rankings.
    The model must compare all ideas and rank them relative to each other.
    
    Rank each joke idea between 1-N. 
    Rank 1 is the most unique and funniest.
    """
    joke_idea: List[JokeIdea] = dspy.InputField()
    joke_rankings: List[int] = dspy.OutputField(description="Rank between 1, 2, 3 ... N")


# ============================================================================
# Parallel Generation and Selection Module
# ============================================================================

class ConditionalJokeGenerator(dspy.Module):
    """
    A joke generator that uses parallel generation and selection.
    
    Process:
    1. Generate multiple joke ideas in parallel (async)
    2. Judge and rank all ideas
    3. Select the best-ranked idea (rank 1)
    4. Expand the selected idea into a full joke
    
    Note: Using async (aforward, acall) allows parallel generation,
    which is much faster than generating sequentially.
    """
    
    def __init__(self, num_samples=5):
        """
        Initialize the components.
        
        Args:
            num_samples: Number of parallel candidates to generate
        """
        self.query_to_idea = dspy.Predict(QueryToIdea)
        self.idea_to_joke = dspy.Predict(IdeaToJoke)
        
        # ChainOfThought helps the model reason about quality before ranking
        self.judge = dspy.ChainOfThought(JokeJudge)
        
        self.num_samples = num_samples

    async def aforward(self, query: str):
        """
        Execute the parallel generation and selection pipeline.
        
        Args:
            query: User's request for a joke
            
        Returns:
            The final joke based on the best-ranked idea
            
        Note: This method is async to enable parallel generation.
        Use await generator.acall(...) to call it.
        """
        # Step 1: Generate multiple candidates in parallel
        # asyncio.gather() runs all tasks concurrently, not sequentially
        # This is much faster than a for loop!
        joke_ideas = await asyncio.gather(
            *[
                self.query_to_idea.acall(query=query) 
                for _ in range(self.num_samples)
            ]
        )
        
        print("Generated Joke Ideas: \n", joke_ideas)
        
        # Step 2: Judge and rank all candidates
        # The judge compares all ideas and ranks them (1 = best, N = worst)
        judge_score = self.judge(joke_idea=joke_ideas).joke_rankings
        print("Judge Score for each: ", judge_score)

        # Step 3: Select the best-ranked idea (rank 1)
        best_joke_idea_idx = judge_score.index(1)

        print("Selected Index: ", best_joke_idea_idx)
        selected_joke_idea = joke_ideas[best_joke_idea_idx]
        print("Selected Joke Idea: \n", selected_joke_idea)

        # Step 4: Expand the selected idea into a full joke
        joke = self.idea_to_joke(joke_idea=selected_joke_idea)

        # Optional: Use a different LLM for the final expansion
        # This allows you to use a more capable (but slower/expensive) model
        # only for the final step
        # with dspy.context(lm=dspy.LM("gemini/gemini-1.5-pro")):
        #    joke = self.idea_to_joke(joke_idea=selected_joke_idea)

        return joke


# ============================================================================
# Execution: Async Main Function
# ============================================================================

async def main():
    """
    Main execution function for async code.
    
    Note: Python requires async code to be run with asyncio.run() or
    await in an async context. This is why we use a main() function.
    """
    joke_generator = ConditionalJokeGenerator()
    
    # Use acall() instead of forward() for async modules
    joke = await joke_generator.acall(
        query="Write a joke about AI that has to do with them turning rogue."
    )

    print("---")
    print(joke)


if __name__ == "__main__":
    # asyncio.run() is required to run async functions from synchronous code
    asyncio.run(main())
