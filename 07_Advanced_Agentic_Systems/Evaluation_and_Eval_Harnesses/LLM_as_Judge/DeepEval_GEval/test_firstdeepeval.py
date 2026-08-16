from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval import assert_test
from deepeval.metrics import GEval
from dotenv import load_dotenv, find_dotenv
import os
from deepeval import evaluate

# Load environment variables from .env
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")



def test_correctness():
    correctness_metric = GEval(
        name="Correctness",
        criteria= "Determine if 'actual output' is correct based on the 'expected output'",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5
    )

    test_case = LLMTestCase(
        input="I have a persistent cough and fever. Should I be worried?",
        # Replace this with the actual output from your LLM application
        actual_output="A persistent cough and fever could be a viral infection or something more serious. See a doctor if symptoms worsen or don't improve in a few days.",
        expected_output="A persistent cough and fever could indicate a range of illnesses, from a mild viral infection to more serious conditions like pneumonia or COVID-19. You should seek medical attention if your symptoms worsen, persist for more than a few days, or are accompanied by difficulty breathing, chest pain, or other concerning signs."
    )

    assert(test_case, [correctness_metric]);
    evaluate(test_cases=[test_case], metrics=[correctness_metric])




test_correctness()