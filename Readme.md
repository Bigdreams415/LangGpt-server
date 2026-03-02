# LangGpt Backend API

A comprehensive backend for a language‑learning mobile/web app focused on **Igbo, Yoruba** and **Hausa**. The service is built with FastAPI, uses Google Gemini for AI generation, and includes full user authentication, progress tracking and content‑generation endpoints.

---

## Repository layout

```
/ (workspace root)
├── README.md                        # this file
├── requirements.txt                 # Python dependencies
├── .env                             # environment variables (not checked in)
├── app/                             # main application package
│   ├── main.py                      # FastAPI application & route registration
│   ├── core/                        # framework and infrastructure
│   │   ├── config/
│   │   │   └── settings.py          # pydantic settings from .env
│   │   ├── database/
│   │   │   ├── database.py          # SQLAlchemy async engine & session
│   │   │   └── redis.py             # Redis client + key helpers
│   │   └── security/
│   │       └── jwt.py               # JWT helpers (create/verify tokens)
│   ├── routers/                     # FastAPI routers (endpoints)
│   │   ├── auth.py                  # signup/login/google/refresh/logout/me
│   │   ├── user_routes.py           # profile CRUD, password change, delete
│   │   ├── lessons.py               # lesson generation & translation
│   │   ├── quiz.py                  # quiz generation & answer checking
│   │   ├── conversation.py          # conversational practice endpoint
│   │   └── progress.py              # user progress (in‑memory for now)
│   ├── models/                      # database models & shared enums
│   │   ├── schemas.py               # request/response Pydantic schemas
│   │   └── user_model.py            # SQLAlchemy user and progress tables
│   ├── prompts/
│   │   └── templates.py             # prompt builders for Gemini
│   ├── schemas/                     # additional Pydantic schemas
│   │   └── auth_schemas.py          # auth/login/signup/profile models
│   └── services/
│       ├── gemini.py                # wrapper around Google Gemini API
│       └── auth_service.py          # business logic for authentication
└── password/                        # small helper library used by auth code
    ├── common/
    │   └── dependencies/
    │       └── auth_dependencies.py # FastAPI security dependencies
    └── dependency/
        └── exceptions/
            └── auth_exceptions.py   # HTTPException helpers
```

> 🔧 **Note:** `__pycache__` directories are omitted for brevity.

---

## Getting started

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate           # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Populate `.env`** (see `app/core/config/settings.py` for available keys).
   ```bash
   cp .env.example .env
   # required fields
   GEMINI_API_KEY=...
   JWT_SECRET_KEY=...                # `openssl rand -hex 32`
   POSTGRES_PASSWORD=...             # if using a local DB
   GOOGLE_CLIENT_ID=...              # for Google OAuth
   ```

3. **Run PostgreSQL & Redis** (or point `settings` to managed instances).
   The app will automatically create tables on startup if they don't exist.

4. **Start the development server**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Browse the interactive docs**
   `http://localhost:8000/docs` (Swagger) or `/redoc`.


---

## Environment variables

The following keys are read from `.env` (defaults shown in `settings.py`):

| Variable                  | Description                                 | Example              |
|--------------------------|---------------------------------------------|----------------------|
| `GEMINI_API_KEY`         | Google Gemini API key                       | `abc123`             |
| `JWT_SECRET_KEY`         | Secret used to sign JWTs                    | generated with openssl |
| `POSTGRES_*`             | Database connection details                 | see `settings.database_url` |
| `REDIS_*`                | Redis connection details                    |                      |
| `GOOGLE_CLIENT_ID`/`SECRET` | OAuth credentials for Google login       |                      |
| `ALLOWED_ORIGINS`        | CORS whitelist, comma‑separated             | `http://localhost:3000` |
| ...                      | other tuning values (rate limit, token expiry) |                   |

> ⚠️ Ensure sensitive values are kept out of source control.

---

## API endpoints

### Authentication (`/auth` prefix)

- `POST /auth/signup` – register with email/password
- `POST /auth/login` – login using email or username
- `POST /auth/google` – sign in/up with Google ID token
- `POST /auth/refresh` – rotate access/refresh tokens
- `POST /auth/logout` – invalidate current tokens
- `GET /auth/me` – return current user profile

### User profile (`/auth/me` & `/auth/me/*` also available via `user_routes`)

- `GET /auth/me` – same as above
- `PATCH /auth/me` – update fields (name, country, language, etc)
- `POST /auth/me/change-password` – change user password
- `DELETE /auth/me` – soft‑delete account

> All profile routes require a valid bearer access token (see `password/common/dependencies/auth_dependencies.py`).

### Lesson & translation (`/lessons`)

- `POST /lessons/` – generate a vocabulary lesson
- `POST /lessons/translate` – translate arbitrary text
- `GET /lessons/topics` – list available lesson topics
- `GET /lessons/languages` – metadata about supported languages

### Quiz (`/quiz`)

- `POST /quiz/` – generate multiple choice questions
- `POST /quiz/check` – evaluate a user's answer

### Conversation (`/conversation`)

- `POST /conversation/` – chat with the AI tutor, maintaining history

### Progress tracking (`/progress`)

- `POST /progress/update` – record a score for a user/topic
- `GET /progress/{user_id}/{language}` – fetch stored progress

> Progress is currently kept in memory; a database implementation exists in `UserProgress` model and can be wired in later.


---

## Data models & schemas

Pydantic models reside in `app/models/schemas.py` and `app/schemas/auth_schemas.py`.
They define request/response shapes, enumeration values, and validation logic.

Database tables are defined using SQLAlchemy in `app/models/user_model.py`.

---

## AI prompt templates

Reusable prompt generators for Gemini are centralised in `app/prompts/templates.py`.
Adjusting content or adding new prompts (e.g. for grammar drills) can be done here.

---

## Future work / notes ✅

1. Persist progress in the database using `UserProgress` model and replace in-memory store.
2. Add email verification, password reset flows (Redis keys already defined).
3. Implement rate limiting using Redis (helper keys exist).
4. Add unit/integration tests and CI pipeline.
5. Dockerize and prepare for cloud deployment.

---

### License & attribution

[MIT License](LICENSE) (if applicable).

Happy coding! 🚀

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