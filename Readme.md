# LangGpt Backend API

A language learning backend for Igbo, Yoruba, and Hausa — built with FastAPI and Google Gemini.

## Project Structure

```
language_app/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── lessons.py           # Vocabulary lessons + translation
│   │   ├── quiz.py              # Quiz generation + answer checking
│   │   ├── conversation.py      # AI conversation partner
│   │   └── progress.py          # User progress tracking
│   ├── models/
│   │   └── schemas.py           # All Pydantic request/response models
│   ├── services/
│   │   └── gemini.py            # Google Gemini AI wrapper
│   └── prompts/
│       └── templates.py         # All prompt templates
├── requirements.txt
└── .env
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create your `.env` file**
   ```bash
   cp .env.example .env
   # Then add your Gemini API key inside .env
   ```
   Get a free API key at: https://aistudio.google.com/apikey

3. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Open API docs**
   ```
   http://localhost:8000/docs
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/lessons/` | Generate a vocabulary lesson |
| POST | `/lessons/translate` | Translate text |
| GET | `/lessons/topics` | List all topics |
| GET | `/lessons/languages` | List supported languages |
| POST | `/quiz/` | Generate a quiz |
| POST | `/quiz/check` | Check a user's answer |
| POST | `/conversation/` | Chat with AI tutor |
| POST | `/progress/update` | Save quiz/lesson score |
| GET | `/progress/{user_id}/{language}` | Get user progress |

## Example Requests

### Get a Lesson
```json
POST /lessons/
{
  "language": "Igbo",
  "level": "beginner",
  "topic": "greetings"
}
```

### Generate a Quiz
```json
POST /quiz/
{
  "language": "Yoruba",
  "level": "beginner",
  "topic": "numbers",
  "num_questions": 5
}
```

### Conversation Practice
```json
POST /conversation/
{
  "language": "Hausa",
  "level": "beginner",
  "topic": "greetings",
  "user_message": "Ina kwana",
  "conversation_history": []
}
```