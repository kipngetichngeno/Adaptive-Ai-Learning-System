from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from pydantic import BaseModel
import models
import database
import ai_tutor
import datetime as dt

app = FastAPI(title="Adaptive AI Learning System")

# ---------------------------------------------------
# FIXED CORS CONFIGURATION - MUST BE FIRST
# ---------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "*"],  # Added specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Added this
)

# ---------------------------------------------------
# CREATE DATABASE TABLES
# ---------------------------------------------------
models.Base.metadata.create_all(bind=database.engine)


# ---------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------
class SubmitAnswerRequest(BaseModel):
    student_id: int
    question_id: int
    student_answer: str


# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------
@app.get("/health")
@app.options("/health")  # Add OPTIONS handler
async def health_check():
    return JSONResponse(
        content={
            "status": "online",
            "message": "Backend is running"
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


# ---------------------------------------------------
# ADAPTIVE DIFFICULTY FUNCTION
# ---------------------------------------------------
def get_next_difficulty(current_difficulty: str, is_correct: bool):
    levels = ["beginner", "intermediate", "advanced"]

    if current_difficulty not in levels:
        return "beginner"

    index = levels.index(current_difficulty)

    if is_correct and index < len(levels) - 1:
        return levels[index + 1]

    if not is_correct and index > 0:
        return levels[index - 1]

    return current_difficulty


# ---------------------------------------------------
# 1. GENERATE QUESTION
# ---------------------------------------------------
@app.get("/generate-question")
@app.options("/generate-question")  # Add OPTIONS handler
async def get_question(topic: str, difficulty: str = "beginner", db: Session = Depends(database.get_db)):
    try:
        question_data = ai_tutor.generate_new_question(topic, difficulty)

        if "error" in question_data:
            return JSONResponse(
                status_code=400,
                content=question_data,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )

        new_question = models.Question(
            topic=topic,
            difficulty=difficulty,
            question=question_data["question"],
            option_a=question_data["options"]["A"],
            option_b=question_data["options"]["B"],
            option_c=question_data["options"]["C"],
            option_d=question_data["options"]["D"],
            correct_answer=question_data["correct_answer"]
        )

        db.add(new_question)
        db.commit()
        db.refresh(new_question)

        return JSONResponse(
            content={
                "question_id": new_question.id,
                "topic": topic,
                "difficulty": difficulty,
                "question": new_question.question,
                "options": {
                    "A": new_question.option_a,
                    "B": new_question.option_b,
                    "C": new_question.option_c,
                    "D": new_question.option_d
                }
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )


# ---------------------------------------------------
# 2. SUBMIT ANSWER
# ---------------------------------------------------
@app.post("/submit-answer")
@app.options("/submit-answer")  # Add OPTIONS handler
async def submit_answer(request: SubmitAnswerRequest, db: Session = Depends(database.get_db)):
    try:
        student_id = request.student_id
        question_id = request.question_id

        # Normalize answer
        student_answer = request.student_answer.strip().upper()

        # Get question
        question = db.query(models.Question).filter(models.Question.id == question_id).first()

        if not question:
            return JSONResponse(
                status_code=404,
                content={"error": "Question not found"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )

        # Get or create student
        student = db.query(models.Student).filter(models.Student.id == student_id).first()

        if not student:
            student = models.Student(
                id=student_id,
                name=f"Student_{student_id}",
                email=None,
                joined_at=dt.datetime.utcnow()
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        correct_answer = question.correct_answer.strip().upper()

        # Check correctness
        is_correct = student_answer == correct_answer

        # Generate AI feedback
        feedback = ai_tutor.get_ai_feedback(
            question.topic,
            question.question,
            student_answer,
            correct_answer,
            is_correct
        )

        # Save result
        new_result = models.QuizResult(
            student_id=student_id,
            question_id=question_id,
            topic=question.topic,
            question=question.question,
            student_answer=student_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            ai_feedback=feedback
        )

        db.add(new_result)
        db.commit()

        # Adaptive difficulty
        next_difficulty = get_next_difficulty(question.difficulty, is_correct)

        return JSONResponse(
            content={
                "status": "Correct" if is_correct else "Incorrect",
                "correct_answer": correct_answer,
                "ai_feedback": feedback,
                "next_difficulty": next_difficulty
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )


# ---------------------------------------------------
# 3. TEACHER ANALYTICS
# ---------------------------------------------------
@app.get("/analytics/struggling-students")
@app.options("/analytics/struggling-students")  # Add OPTIONS handler
async def get_struggling_students(db: Session = Depends(database.get_db)):
    try:
        results = (
            db.query(
                models.Student.name,
                func.avg(models.QuizResult.is_correct.cast(Integer)).label("avg_score")
            )
            .join(models.QuizResult)
            .group_by(models.Student.id)
            .having(func.avg(models.QuizResult.is_correct.cast(Integer)) < 0.6)
            .all()
        )

        return JSONResponse(
            content=[
                {
                    "name": r.name,
                    "score": f"{round(r.avg_score * 100, 2)}%"
                }
                for r in results
            ],
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )