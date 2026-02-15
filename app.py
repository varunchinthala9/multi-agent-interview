import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key (for local use)
load_dotenv()

# SAFE client initialization (works in Streamlit Cloud and locally)
def get_openai_client():
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    elif os.getenv("OPENAI_API_KEY"):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    else:
        st.error("OpenAI API key not found. Please configure Secrets.")
        st.stop()

client = get_openai_client()

st.title("Multi-Agent Interview Simulator")

# -------- INPUT SECTIONS --------

st.header("Context")

context_text = st.text_area("Job Description and Company Info")

st.header("Candidate")

candidate_text = st.text_area("Candidate Resume and Info")

st.header("Interviewer")

interviewer_text = st.text_area("Interviewer Info")

st.header("Settings")

num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=3)


# -------- AGENT FUNCTION --------

def create_agent_response(system_prompt, message):

    full_input = f"""
{system_prompt}

{message}
"""

    response = client.responses.create(
        model="gpt-5-nano",
        input=full_input
    )

    return response.output_text


# -------- BUTTON ACTION --------

if st.button("Start Interview"):

    # -------- Interview phases --------

    interview_phases = [
        "INTRODUCTION",
        "BACKGROUND",
        "TECHNICAL_DEEP_DIVE",
        "BEHAVIORAL",
        "CANDIDATE_QUESTIONS",
        "CLOSING"
    ]

    # -------- Candidate prompt --------

    candidate_prompt = f"""
You are a job candidate in a live interview.

Your resume:
{candidate_text}

Job context:
{context_text}

INTERVIEW BEHAVIOR RULES:

You must behave exactly like a real candidate.

1. Answer questions naturally and professionally
2. Keep answers concise (2–5 sentences), do not give too much longer explanations. 
3. Speak conversationally
4. Do NOT give essays
5. Do NOT give structured reports
6. Give realistic answers based on your resume and experience. 
7. If interviewer asks closing question, respond professionally

Tone:
- Professional
- Confident
- Natural
- Human-like
"""

    # -------- Interviewer prompt --------

    interviewer_prompt = f"""
You are a Senior interviewer conducting a real live job interview.

You have already reviewed the candidate's resume.

Your info:
{interviewer_text}

Job context:
{context_text}

Candidate resume:
{candidate_text}

INTERVIEW BEHAVIOR RULES:

You must behave exactly like a real interviewer.

Interview structure:

1. First message:
   - Brief greeting
   - Introduce yourself in 1 sentence
   - Explain interview format briefly
   - Ask the first question

2. During interview:
   - Ask only ONE question at a time
   - Questions should be open-ended
   - Questions should relate to the job description, tasks,required skills and candidate's experience
   - Ask natural follow-up questions based on answers
   - Keep each message under 4 sentences

3. Tone:
   - Professional
   - Neutral
   - Conversational
   - Not robotic

4. DO NOT:
   - Do NOT write long reports
   - Do NOT analyze candidate performance
   - Do NOT ask multiple questions at once
   - Do NOT explain what you are doing

5. Final round:
   - Ask if candidate has questions
   - Then close interview professionally
"""

    st.write("Agents created successfully.")
    st.subheader("Interview Begins")

    # -------- Conversation memory --------

    conversation_history = ""
    conversation_history += "This is the start of the interview.\n"

    # -------- Interview loop --------

    for i in range(num_questions):

        phase_index = min(i, len(interview_phases) - 1)
        current_phase = interview_phases[phase_index]

        interviewer_input = f"""
Interview Phase: {current_phase}

Conversation so far:
{conversation_history}

Instructions based on phase:

INTRODUCTION:
- Greet candidate
- Introduce yourself
- Ask first general question

BACKGROUND:
- Ask about candidate experience and past projects

TECHNICAL_DEEP_DIVE:
- Ask technical questions based on resume and previous answers
- Ask follow-up questions

BEHAVIORAL:
- Ask behavioral questions (teamwork, challenges, conflict, decisions)

CANDIDATE_QUESTIONS:
- Ask candidate if they have questions for you

CLOSING:
- Thank the candidate
- Close interview professionally

Important rules:
- Do NOT repeat questions
- Do NOT restart interview
- Ask only ONE question at a time
- Be conversational and realistic
"""

        interviewer_question = create_agent_response(
            interviewer_prompt,
            interviewer_input
        )

        st.markdown(f"**Interviewer (Question {i+1}):**")
        st.write(interviewer_question)

        conversation_history += f"\nInterviewer: {interviewer_question}\n"

        candidate_input = f"""
Conversation so far:
{conversation_history}

Answer the interviewer's latest question naturally.
Do NOT repeat previous answers.
"""

        candidate_answer = create_agent_response(
            candidate_prompt,
            candidate_input
        )

        st.markdown(f"**Candidate (Answer {i+1}):**")
        st.write(candidate_answer)

        conversation_history += f"\nCandidate: {candidate_answer}\n"
