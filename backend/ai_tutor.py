import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ----------------------------------------
# AI FEEDBACK FUNCTION
# ----------------------------------------
def get_ai_feedback(topic, question, student_answer, correct_answer, is_correct):
    """
    Generates personalized AI tutor feedback for the student.
    """

    if is_correct:
        prompt = (
            f"The student correctly answered this {topic} question: '{question}'. "
            f"Give a short praise message and one interesting advanced fact "
            f"related to {topic}. Keep it under 2 sentences."
        )
    else:
        prompt = (
            f"A student is learning {topic}. "
            f"The question was: '{question}'. "
            f"The student answered: '{student_answer}'. "
            f"The correct answer is: '{correct_answer}'. "
            f"Explain the concept simply so the student can understand their mistake. "
            f"Do not just repeat the correct answer. Keep it supportive and under 3 sentences."
        )

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI tutor temporarily unavailable: {str(e)}"


# ----------------------------------------
# QUESTION GENERATION FUNCTION
# ----------------------------------------
def generate_new_question(topic: str, difficulty: str = "beginner"):
    """
    Generates an AI multiple choice question.
    """

    prompt = (
        f"You are an AI tutor. Generate ONE multiple-choice question about {topic} "
        f"for a {difficulty} level student.\n\n"
        f"Rules:\n"
        f"- Provide exactly 4 options labelled A, B, C, D\n"
        f"- Indicate the correct option\n"
        f"- Return ONLY JSON\n\n"
        f"JSON format:\n"
        f'{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "A"}}'
    )

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.6
        )

        data = json.loads(response.choices[0].message.content)

        # Safety check
        if "question" not in data or "options" not in data or "correct_answer" not in data:
            return {"error": "Invalid AI response format"}

        return data

    except Exception as e:
        return {"error": str(e)}