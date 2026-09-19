import streamlit as st
import asyncio
import whisper
import tempfile
import os
from interview_practice_system import (
    initialize_preparation_crew,
    evaluate_answer,
    generate_follow_up_question,
)
from streamlit_mic_recorder import mic_recorder

st.title("🤖 AI Mock Interviewer")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.interview_started = False
    st.session_state.current_question = None
    st.session_state.current_answer = None
    st.session_state.evaluation = None
    st.session_state.preparation_crew = None
    st.session_state.follow_up_question = None
    st.session_state.is_generating_follow_up = False

# Sidebar for interview setup
with st.sidebar:
    st.header("Interview Setup")
    company_name = st.text_input("Company Name", "Google")
    role = st.text_input("Position", "Software Engineer")
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)

    if st.button("Start Interview"):
        st.session_state.interview_started = True
        st.session_state.messages = []
        st.session_state.current_question = None
        st.session_state.current_answer = None
        st.session_state.evaluation = None
        st.session_state.follow_up_question = None
        st.session_state.is_generating_follow_up = False

        # Initialize the preparation crew
        st.session_state.preparation_crew = initialize_preparation_crew(
            company_name, role, difficulty
        )
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Start interview if not started
if not st.session_state.interview_started:
    st.info(
        "👋 Welcome! Please set up your interview in the sidebar and click 'Start Interview' to begin."
    )
else:
    # If we don't have a current question, start the interview
    if st.session_state.current_question is None:
        with st.spinner("🤖 Preparing your interview question..."):
            # Execute the preparation crew to get the question and correct answer
            preparation_result = st.session_state.preparation_crew.kickoff()

            # Store the question and correct answer
            st.session_state.current_question = preparation_result.pydantic.question
            st.session_state.correct_answer = preparation_result.pydantic.correct_answer

            # Add the question to the chat
            st.session_state.messages.append(
                {"role": "assistant", "content": st.session_state.current_question}
            )
            st.rerun()

# Get user input
input_method = st.radio("Choose your input method:", ["Text", "Voice"], horizontal=True)

user_input = None  # Initialize user_input


def convert_speech_to_text(audio_bytes):
    try:
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        try:
            # Load the Whisper model (this will download the model on first run)
            model = whisper.load_model("base")

            # Transcribe the audio
            result = model.transcribe(temp_audio_path)
            return result["text"]
        finally:
            # Clean up the temporary file
            os.unlink(temp_audio_path)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None


if input_method == "Text":
    user_input = st.chat_input("Type your answer...")
else:
    st.write("Click the microphone to record your answer:")
    audio = mic_recorder(
        start_prompt="🎤 Start recording",
        stop_prompt="⏹️ Stop recording",
        just_once=True,
        use_container_width=True,
    )

    if audio:
        with st.spinner("Converting speech to text..."):
            # Convert the audio bytes to text
            user_input = convert_speech_to_text(audio["bytes"])
            if user_input:
                st.success(f"Recognized: {user_input}")
            else:
                st.error("Could not recognize speech. Please try again.")

if user_input is not None:
    # Add user's answer to messages
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Store the answer
    st.session_state.current_answer = user_input

    # Show thinking message
    with st.spinner("🤖 Evaluating your answer..."):
        # Evaluate the answer
        evaluation = evaluate_answer(
            question=st.session_state.current_question,
            user_answer=user_input,
            correct_answer=st.session_state.correct_answer,
        )

        # Add the evaluation to the chat
        st.session_state.messages.append({"role": "assistant", "content": evaluation})

        # Generate follow-up question if not already generating
        if not st.session_state.is_generating_follow_up:
            st.session_state.is_generating_follow_up = True
            try:
                # Generate follow-up question
                follow_up_result = asyncio.run(
                    generate_follow_up_question(
                        question=st.session_state.current_question,
                        user_answer=user_input,  # Pass the user's answer for context
                        company_name=company_name,
                        role=role,
                        difficulty=difficulty.lower(),
                    )
                )

                # Store the follow-up question
                st.session_state.follow_up_question = follow_up_result

                # Add the follow-up question to the chat
                st.session_state.messages.append(
                    {"role": "assistant", "content": follow_up_result.question}
                )

                # Set up for the follow-up question
                st.session_state.current_question = follow_up_result.question
                st.session_state.correct_answer = follow_up_result.correct_answer
            except Exception as e:
                st.error(f"Error generating follow-up question: {str(e)}")
                st.session_state.current_question = None
                st.session_state.current_answer = None
        else:
            # Reset for next question
            st.session_state.current_question = None
            st.session_state.current_answer = None

        st.session_state.is_generating_follow_up = False
        st.rerun()

# Auto-scroll
scroll_placeholder = st.empty()
