from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
import asyncio


class QuestionAnswerPair(BaseModel):
    """Schema for the question and its correct answer."""

    question: str = Field(..., description="The technical question to be asked")
    correct_answer: str = Field(..., description="The correct answer to the question")


# Initialize the search tool
search_tool = SerperDevTool()

# First Crew: Question Preparation
# Create the company research agent
company_researcher = Agent(
    role="Company Research Specialist",
    goal="Gather information about the company and create interview questions with answers",
    backstory="""You are an expert in researching companies and creating technical interview questions.
    You have deep knowledge of tech industry hiring practices and can create relevant
    questions that test both theoretical knowledge and practical skills.""",
    tools=[search_tool],
    verbose=True,
)

# Create the question preparer agent
question_preparer = Agent(
    role="Question and Answer Preparer",
    goal="Prepare comprehensive questions with model answers",
    backstory="""You are an experienced technical interviewer who knows how to create
    challenging yet fair technical questions and provide detailed model answers.
    You understand how to assess different skill levels and create questions that
    test both theoretical knowledge and practical problem-solving abilities.""",
    verbose=True,
)

# Second Crew: Answer Evaluation
# Create the answer evaluator agent
answer_evaluator = Agent(
    role="Answer Evaluator",
    goal="Evaluate if the given answer is correct for the question",
    backstory="""You are a senior technical interviewer who evaluates answers
    against the expected solution. You know how to identify if an answer is
    technically correct and complete.""",
    verbose=True,
)

# Create the follow-up question agent
follow_up_questioner = Agent(
    role="Follow-up Question Specialist",
    goal="Create relevant follow-up questions based on the context",
    backstory="""You are an expert technical interviewer who knows how to create
    meaningful follow-up questions that probe deeper into a candidate's knowledge
    and understanding. You can create questions that build upon previous answers
    and test different aspects of the candidate's technical expertise.""",
    verbose=True,
)

# Create the new topic question agent
new_topic_questioner = Agent(
    role="New Topic Question Specialist",
    goal="Create interview questions on new technical topics",
    backstory="""You are an expert technical interviewer who knows how to create
    diverse interview questions across different technical domains. You can identify
    new topics that haven't been covered yet and create questions that test
    different aspects of a candidate's technical knowledge and skills.""",
    verbose=True,
)

# Maximum number of follow-up questions per topic
MAX_FOLLOWUPS_PER_TOPIC = 3


# Create tasks for the first crew
def create_company_research_task(company_name: str, role: str, difficulty: str) -> Task:
    return Task(
        description=f"""Research {company_name} and gather information about:
        1. Their technical interview process
        2. Common interview questions for {role} positions at {difficulty} difficulty level
        3. Technical stack and requirements
        
        Provide a summary of your findings.""",
        expected_output="A report about the company's technical requirements and interview process",
        agent=company_researcher,
    )


def create_question_preparation_task(difficulty: str) -> Task:
    return Task(
        description=f"""Based on the company research, create:
        1. A technical question at {difficulty} difficulty level that tests both theory and practice
        2. A comprehensive model answer that covers all key points
        3. Key points to look for in candidate answers
        
        The question should be appropriate for {difficulty} difficulty level - challenging but fair, and the answer should be detailed.""",
        expected_output="A question and its correct answer",
        output_pydantic=QuestionAnswerPair,
        agent=question_preparer,
    )


# Create task for the second crew
def create_evaluation_task(
    question: str, user_answer: str, correct_answer: str
) -> Task:
    return Task(
        description=f"""Evaluate if the given answer is correct for the question:
        Question: {question}
        Answer: {user_answer}
        Correct Answer: {correct_answer}
        Provide:
        1. Whether the answer is correct (Yes/No)
        2. Key points that were correct or missing
        3. A brief explanation of why the answer is correct or incorrect""",
        expected_output="Evaluation of whether the answer is correct for the question with feedback",
        agent=answer_evaluator,
    )

# Updated to include user_answer
def create_follow_up_question_task(
    question: str, user_answer: str, company_name: str, role: str, difficulty: str
) -> Task:
    return Task(
        description=f"""Based on the context, create a relevant follow-up question:
        Original Question: {question}
        Candidate's Answer: {user_answer}
        Company: {company_name}
        Role: {role}
        Difficulty: {difficulty}
        
        Create a follow-up question that:
        1. Builds upon the original question
        2. Tests deeper understanding of the topic
        3. Is appropriate for the specified difficulty level
        4. Is relevant to the company and role
        
        The follow-up question should be challenging but fair, and should help
        assess the candidate's technical depth and problem-solving abilities.""",
        expected_output="A follow-up question that builds upon the candidate's specific answer",
        output_pydantic=QuestionAnswerPair,
        agent=follow_up_questioner,
    )


# Task for generating a new topic question
def create_new_topic_question_task(
    company_name: str, role: str, difficulty: str, covered_topics: list[str]
) -> Task:
    topics_str = ", ".join(covered_topics) if covered_topics else "None yet"
    return Task(
        description=f"""Create a NEW interview question on a DIFFERENT technical topic:
        Company: {company_name}
        Role: {role}
        Difficulty: {difficulty}
        Topics Already Covered: {topics_str}
        
        Create a question that:
        1. Is on a COMPLETELY DIFFERENT topic from those already covered
        2. Tests a different area of technical knowledge relevant to the role
        3. Is appropriate for the specified difficulty level
        4. Is relevant to the company and role
        
        Choose from different domains like: SQL, Python coding, statistics, 
        machine learning, data structures, system design, data pipelines, 
        cloud services, algorithms, etc.
        
        The question should be challenging but fair for the difficulty level.""",
        expected_output="A new question on a different topic with its correct answer",
        output_pydantic=QuestionAnswerPair,
        agent=new_topic_questioner,
    )


def create_follow_up_crew(
    question: str, company_name: str, role: str, difficulty: str
) -> Crew:
    """Initialize the crew responsible for creating follow-up questions."""
    crew = Crew(
        agents=[follow_up_questioner],
        tasks=[
            create_follow_up_question_task(question, company_name, role, difficulty),
        ],
        process=Process.sequential,
        verbose=True,
    )
    return crew


async def generate_follow_up_question(
    question: str, user_answer: str, company_name: str, role: str, difficulty: str
) -> QuestionAnswerPair:
    crew = Crew(
        agents=[follow_up_questioner],
        tasks=[
            # Pass user_answer here
            create_follow_up_question_task(question, user_answer, company_name, role, difficulty),
        ],
        process=Process.sequential,
        verbose=True,
    )
    result = await crew.kickoff_async()
    return result.pydantic


async def generate_new_topic_question(
    company_name: str, role: str, difficulty: str, covered_topics: list[str]
) -> QuestionAnswerPair:
    """Generate a new question on a different topic."""
    crew = Crew(
        agents=[new_topic_questioner],
        tasks=[
            create_new_topic_question_task(company_name, role, difficulty, covered_topics),
        ],
        process=Process.sequential,
        verbose=True,
    )
    result = await crew.kickoff_async()
    return result.pydantic


def extract_topic_from_question(question: str) -> str:
    """Extract a brief topic identifier from a question for tracking."""
    # Take first 50 chars as a simple topic identifier
    return question[:50].strip() + "..."


async def start_interview_practice(
    company_name: str, role: str, difficulty: str = "easy"
):
    # ---------------------------------------------------------
    # 1. PREPARATION PHASE (Silent)
    # ---------------------------------------------------------
    print(f"Researching {company_name} and preparing your question... (this may take a moment)")
    
    # Set verbose=False here to hide the 'Correct Answer' from the console
    preparation_crew = Crew(
        agents=[company_researcher, question_preparer],
        tasks=[
            create_company_research_task(company_name, role, difficulty),
            create_question_preparation_task(difficulty),
        ],
        process=Process.sequential,
        verbose=False,  # <--- CRITICAL CHANGE: Prevents spoilers
    )

    # This runs synchronously because we CANNOT proceed without the question
    preparation_result = preparation_crew.kickoff()
    
    # Extract data safely
    try:
        current_question = preparation_result.pydantic.question
        correct_answer = preparation_result.pydantic.correct_answer
    except AttributeError:
        # Fallback if pydantic parsing fails
        current_question = str(preparation_result)
        correct_answer = "Model answer not available."

    # Tracking variables
    question_number = 1
    topic_number = 1
    follow_up_count = 0  # Count of follow-ups for current topic
    covered_topics: list[str] = [extract_topic_from_question(current_question)]
    
    # ---------------------------------------------------------
    # CONTINUOUS INTERVIEW LOOP
    # ---------------------------------------------------------
    while True:
        # Determine if this is a new topic or a follow-up
        is_new_topic = follow_up_count == 0
        
        # ---------------------------------------------------------
        # 2. USER INTERACTION
        # ---------------------------------------------------------
        print("\n" + "="*50)
        if is_new_topic:
            print(f"📚 NEW TOPIC #{topic_number} - QUESTION #{question_number}")
        else:
            print(f"📚 TOPIC #{topic_number} - FOLLOW-UP {follow_up_count}/{MAX_FOLLOWUPS_PER_TOPIC} - QUESTION #{question_number}")
        print("="*50)
        print(current_question)
        print("="*50)
        print("\n(Type 'quit' or 'exit' to end the interview session)\n")
        
        # The code effectively pauses here for user input
        user_answer = input("Your answer: ")
        
        # Check for exit commands
        if user_answer.lower().strip() in ['quit', 'exit', 'q']:
            print("\n" + "="*50)
            print("INTERVIEW SESSION ENDED")
            print("="*50)
            print(f"You completed {question_number - 1} question(s) across {topic_number} topic(s).")
            print("Thank you for practicing! Good luck with your interview!")
            print("="*50)
            break

        # ---------------------------------------------------------
        # 3. EVALUATION & NEXT QUESTION GENERATION (Async & Parallel)
        # ---------------------------------------------------------
        
        # Task A: Evaluate (We can use verbose=True here as the user has already answered)
        eval_crew = Crew(
            agents=[answer_evaluator],
            tasks=[create_evaluation_task(current_question, user_answer, correct_answer)],
            verbose=True 
        )
        
        # Task B: Generate next question
        # Check if we've reached max follow-ups for this topic
        if follow_up_count >= MAX_FOLLOWUPS_PER_TOPIC:
            # Switch to a new topic
            print(f"\n🔄 Max follow-ups reached for this topic. Switching to a NEW topic...")
            next_question_task = generate_new_topic_question(
                company_name=company_name,
                role=role,
                difficulty=difficulty,
                covered_topics=covered_topics
            )
        else:
            # Continue with follow-up on same topic
            print("\nAnalyzing your answer and generating follow-up...")
            next_question_task = generate_follow_up_question(
                question=current_question,
                user_answer=user_answer,
                company_name=company_name,
                role=role,
                difficulty=difficulty
            )

        # Run both simultaneously
        evaluation_result, next_question_result = await asyncio.gather(
            eval_crew.kickoff_async(),
            next_question_task
        )

        # ---------------------------------------------------------
        # 4. DISPLAY EVALUATION RESULTS
        # ---------------------------------------------------------
        # Evaluation result is printed automatically by verbose=True in eval_crew

        input("\nPress Enter to continue to the next question...")

        # ---------------------------------------------------------
        # 5. PREPARE NEXT QUESTION
        # ---------------------------------------------------------
        try:
            current_question = next_question_result.question
            correct_answer = next_question_result.correct_answer
        except AttributeError:
            current_question = str(next_question_result)
            correct_answer = "Model answer not available."
        
        # Update counters
        if follow_up_count >= MAX_FOLLOWUPS_PER_TOPIC:
            # Reset for new topic
            follow_up_count = 0
            topic_number += 1
            covered_topics.append(extract_topic_from_question(current_question))
        else:
            # Increment follow-up count
            follow_up_count += 1
        
        question_number += 1


if __name__ == "__main__":
    company = "Google"
    role = "Data Scientist"
    print(f"Starting mock interview practice for {role} position at {company}...")
    asyncio.run(start_interview_practice(company, role))


# ------------------------------------------------------------------------------------------------
# For the Streamlit app
# ------------------------------------------------------------------------------------------------
def initialize_preparation_crew(company_name: str, role: str, difficulty: str) -> Crew:
    """Initialize the crew responsible for preparing interview questions."""
    return Crew(
        agents=[company_researcher, question_preparer],
        tasks=[
            create_company_research_task(company_name, role, difficulty),
            create_question_preparation_task(difficulty),
        ],
        process=Process.sequential,
        verbose=True,
    )


def evaluate_answer(question: str, user_answer: str, correct_answer: str) -> str:
    """Create and execute the evaluation crew to assess the user's answer."""
    evaluation_crew = Crew(
        agents=[answer_evaluator],
        tasks=[
            create_evaluation_task(
                question=question,
                user_answer=user_answer,
                correct_answer=correct_answer,
            )
        ],
        process=Process.sequential,
        verbose=True,
    )
    return evaluation_crew.kickoff()
