import pytest
import pandas as pd
import asyncio
from ragas import SingleTurnSample
from ragas.metrics import LLMContextPrecisionWithoutReference
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
import requests
import os
from dotenv import load_dotenv, find_dotenv

# Load API Key
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Constants
EXCEL_FILE = "D:\\Blogs\\Eval\\Eval_LLM\\Ragas\\test_questions.xlsx"
BACKEND_URL = "http://localhost:8000"

# Load models
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
evaluator_llm = LangchainLLMWrapper(llm)

@pytest.mark.parametrize("row", pd.read_excel(EXCEL_FILE).iterrows())
def test_context_precision(row):
    index, data = row
    question = data["question"]

    # Step 1: Ask the RAG backend
    response_rag = requests.post(f"{BACKEND_URL}/ask", data={"prompt": question})
    response_data = response_rag.json()

    assert response_rag.status_code == 200, f"API call failed: {response_data}"

    # Step 2: Evaluate with RAGAS
    sample = SingleTurnSample(
        user_input=question,
        response=response_data["answer"],
        retrieved_contexts=[response_data["retrieved_docs"][0]]
    )
    context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)

    score = asyncio.run(context_precision.single_turn_ascore(sample))
    print("Questions=",question)
    print("Response=",response_data["answer"])
    print("Retrieve context", [response_data["retrieved_docs"][0]])
    print("Scores=", score)
    # Step 3: Write score back to Excel
    df = pd.read_excel(EXCEL_FILE)
    df.at[index, "score"] = score
    df.at[index, "answer"] = response_data["answer"]
    df.at[index, "context"] =[response_data["retrieved_docs"][0]]
    df.to_excel(EXCEL_FILE, index=False)

    # Step 4: Assert the score is valid
    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
