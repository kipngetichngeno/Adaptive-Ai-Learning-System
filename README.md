 Adaptive AI Learning System

An intelligent web-based learning platform that generates questions, evaluates student answers, and adapts difficulty levels dynamically using AI.

Project Overview

The Adaptive AI Learning System is designed to enhance personalized learning by:

* Generating AI-powered quiz questions
* Evaluating student responses in real-time
* Providing intelligent feedback
* Adjusting difficulty based on performance
* Offering analytics for educators

This system combines **FastAPI (backend)** and **Vanilla JavaScript (frontend)** to deliver a lightweight and scalable solution.

 Key Features
 AI Question Generation

* Generate questions based on topic and difficulty level
* Multiple-choice format (A, B, C, D)

###  Answer Evaluation

* Instant correctness check
* AI-generated feedback for each answer

###  Adaptive Learning

* Difficulty adjusts automatically:

  * Correct → harder questions
  * Incorrect → easier questions

### Teacher Analytics

* Identify struggling students
* View average performance scores

###  Frontend Dashboard

* Clean UI with:

  * Question generation
  * Answer submission
  * Performance analytics

##  Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* Pydantic
* SQLite (or configurable DB)

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript (Fetch API)

##  Project Structure

```
project/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── ai_tutor.py
│   ├── requirements.txt
│   └── env/
│
├── front-end/
│   ├── index.html
│   └── assets/
│       ├── style.css
│       ├── script.js
│       └── favicon.ico
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```
git clone https://github.com/your-username/adaptive-ai-learning.git
cd adaptive-ai-learning
```

---

### 2️⃣ Setup Backend

```
cd backend
python -m venv env
source env/Scripts/activate   # Git Bash
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the backend:

```
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

### 3️⃣ Setup Frontend

Open a new terminal:

```
cd front-end
python -m http.server 5500
```

Open in browser:

```
http://127.0.0.1:5500
```

---

## 🔗 API Endpoints

### Health Check

```
GET /health
```

### Generate Question

```
GET /generate-question?topic=python&difficulty=beginner
```

### Submit Answer

```
POST /submit-answer
```

Body:

```json
{
  "student_id": 123,
  "question_id": 1,
  "student_answer": "A"
}
```

### Analytics

```
GET /analytics/struggling-students
```

---

## 🧪 Usage

1. Enter a topic (e.g., Python, Math)
2. Generate a question
3. Select or type your answer
4. Submit to receive:

   * Correct/Incorrect status
   * AI feedback
   * Suggested next difficulty

##  Future Improvements

* User authentication system
* Dashboard with progress tracking
* Integration with LLM APIs (OpenAI, etc.)
* Support for open-ended questions
* Deployment to cloud (AWS, Render, Vercel)


##  Author

**Enock Ngeno**
Data Analyst | Data Scientist | ML Engineer


## 📄 License

This project is for academic and educational purposes.
