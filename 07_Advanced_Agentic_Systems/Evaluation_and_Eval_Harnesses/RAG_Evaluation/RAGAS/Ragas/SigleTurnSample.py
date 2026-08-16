import asyncio
from ragas import SingleTurnSample
from ragas.metrics import LLMContextPrecisionWithoutReference
from ragas.llms import LangchainLLMWrapper
import os
from dotenv import load_dotenv,find_dotenv
from langchain_openai import ChatOpenAI


# Find API key from .env file
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
evaluator_llm = LangchainLLMWrapper(llm)


async def context_precision():
    sample = SingleTurnSample(
            user_input="Where is the Eiffel Tower located?",
            response="The Eiffel Tower is located in Paris.",
            retrieved_contexts=["The Eiffel Tower is located in Paris."], 
        )

    context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)
    score = await context_precision.single_turn_ascore(sample)
    print(score)

# Call the async function
if __name__ == "__main__":
    asyncio.run(context_precision())
