import asyncio
from ragas import SingleTurnSample
from ragas.metrics import LLMContextRecall, LLMContextPrecisionWithoutReference
from ragas.llms import LangchainLLMWrapper
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Set up the LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
evaluator_llm = LangchainLLMWrapper(llm)

async def evaluate_context_metrics():
    # Create a sample where 4 out of 5 retrieved contexts are relevant
    sample = SingleTurnSample(
        user_input="Where is the Eiffel Tower located?",
        response="The Eiffel Tower is located in Paris.",
        reference="The Eiffel Tower is located in Paris. France is a country of Europe. India is in Asia ",
        retrieved_contexts=["Paris is the capital of France."]
    )

    # Initialize the metrics
    context_recall = LLMContextRecall(llm=evaluator_llm)
    context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)

    # Evaluate both metrics
    recall_score = await context_recall.single_turn_ascore(sample)
    precision_score = await context_precision.single_turn_ascore(sample)

    # Output the scores
    print(f"Context Recall Score: {recall_score:.2f}")
    print(f"Context Precision Score: {precision_score:.2f}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(evaluate_context_metrics())
