import asyncio
from ragas import SingleTurnSample
from ragas.metrics import LLMContextPrecisionWithoutReference
from ragas.llms import LangchainLLMWrapper
import os
from dotenv import load_dotenv,find_dotenv
from langchain_openai import ChatOpenAI
import requests


load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
evaluator_llm = LangchainLLMWrapper(llm)
backend_url = "http://localhost:8000" 

async def context_precision():
    question = "How many years of experience Soumen has?"
    response_rag =requests.post(f"{backend_url}/ask", data={"prompt": question})
    data = response_rag.json()

    sample = SingleTurnSample(
        user_input= question,
        response=data["answer"],
        retrieved_contexts=[data["retrieved_docs"][1]], 
    )
    context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)
    score = await context_precision.single_turn_ascore(sample)
    print(score)

# Call the async function
if __name__ == "__main__":
    asyncio.run(context_precision())