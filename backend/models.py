from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base


# -----------------------------
# STUDENTS TABLE
# -----------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=True)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    results = relationship("QuizResult", back_populates="student")


# -----------------------------
# QUESTIONS TABLE (AI Generated)
# -----------------------------
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    topic = Column(String(100))
    difficulty = Column(String(50))

    question = Column(Text)

    option_a = Column(Text)
    option_b = Column(Text)
    option_c = Column(Text)
    option_d = Column(Text)

    correct_answer = Column(String(5))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# -----------------------------
# QUIZ RESULTS TABLE
# -----------------------------
class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))

    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))

    topic = Column(String(100))
    question = Column(Text)

    student_answer = Column(Text)

    correct_answer = Column(Text)

    is_correct = Column(Boolean)

    ai_feedback = Column(Text)

    time_taken_seconds = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="results")