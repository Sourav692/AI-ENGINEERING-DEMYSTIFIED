from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, SystemMessage

from agent.prompts import (
    COVER_LETTER_PROMPT,
    RESUME_SCORER_PROMPT,
    RESUME_CHECKER_PROMPT,
    CAREER_COACH_SYSTEM_PROMPT,
)


def run_cover_letter(llm: ChatGroq, resume_text: str, job_description: str) -> str:
    """Generate a tailored cover letter. Requires both resume and JD."""
    chain = COVER_LETTER_PROMPT | llm
    result = chain.invoke({
        "job_description": job_description,
        "resume_text": resume_text,
    })
    return result.content


def run_resume_scorer(llm: ChatGroq, resume_text: str, job_description: str) -> str:
    """ATS scoring of resume against a JD. Requires both resume and JD."""
    prompt = RESUME_SCORER_PROMPT.format(
        job_description=job_description,
        resume_text=resume_text,
    )
    result = llm.invoke(prompt)
    return result.content


def run_resume_checker(llm: ChatGroq, resume_text: str) -> str:
    """Standalone resume evaluation. Only needs resume."""
    chain = RESUME_CHECKER_PROMPT | llm
    result = chain.invoke({"resume_text": resume_text})
    return result.content


def run_career_coach(
    llm: ChatGroq, resume_text: str, messages: list[BaseMessage]
) -> str:
    """Career coaching with full conversation context."""
    system_msg = SystemMessage(
        content=CAREER_COACH_SYSTEM_PROMPT.format(resume_text=resume_text)
    )
    result = llm.invoke([system_msg] + messages)
    return result.content
