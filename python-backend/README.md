# 👗 AI Fashion Stylist — StyleMate AI (Python / FastAPI)

An AI-powered fashion stylist chatbot that gives personalized outfit
recommendations based on occasion, style, colors, weather/season, and the
clothing you own. Built **primarily with Python**.

> This folder is the pure-Python reference implementation (FastAPI + SQLite +
> SQLAlchemy + Anthropic Claude SDK). A mirror of the same product also runs as
> a Next.js app in the repository root (that version is what the hosted sandbox
> serves), but **all backend/AI logic here is Python** and runs standalone with
> `uvicorn`.

---

## 1. Project Overview
StyleMate AI behaves like a friendly, professional fashion stylist. It answers
natural-language questions ("What should I wear to an interview?"), generates
structured outfit cards, supports follow-up questions with conversation memory,
and never comments on the user's body or appearance.

## 2. Features
- 🤖 AI fashion chatbot (StyleMate AI) with conversation context
- 👤 User profile for personalization
- ✨ Structured Outfit Generator (top, bottom, shoes, accessories, bag, layering, tips)
- ⚡ Quick prompt buttons
- 💾 Saved outfits (save / rename / delete)
- 🗂️ Chat history (create / view / delete)
- 🎭 DEMO MODE that works with **no API key**
- 🧪 Pytest test suite

## 3. Technologies Used
Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy, SQLite,
python-dotenv, Anthropic Python SDK, Jinja2, HTML/CSS/JS.

## 4. Project Structure
```
python-backend/
├── app/
│   ├── main.py            # FastAPI app + page routes + /api/health
│   ├── config.py          # env + settings (demo mode detection)
│   ├── database.py        # SQLAlchemy engine/session/Base
│   ├── models/            # User, Conversation, Message, SavedOutfit
│   ├── schemas/           # Pydantic request/response models
│   ├── routes/            # chat, conversations, outfits, users
│   ├── services/          # claude_service.py, outfit_service.py
│   └── utils/helpers.py
├── static/{css,js,images}
├── templates/             # index, profile, outfits, history
├── tests/                 # pytest: test_chat.py, test_outfits.py
├── .env / .env.example
├── requirements.txt
└── README.md
```

## 5. Python Installation
Install Python 3.11+ from https://www.python.org/downloads/ and verify:
```
python --version
```

## 6. Virtual Environment Setup
```
cd python-backend
python -m venv venv
```
Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

## 7. Install Dependencies
```
pip install -r requirements.txt
```

## 8. Environment Variables
```
cp .env.example .env        # Windows: copy .env.example .env
```

## 9. Anthropic API Key Configuration
Open `.env` and set:
```
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
```
Get a key at https://console.anthropic.com/.
**Leave it empty to run in DEMO MODE** (rule-based responses, no key needed).
The key is read only on the server via `os.getenv` and is **never exposed to
the frontend**.

## 10. Database Setup
No manual step required — SQLite tables are created automatically on startup
(`init_db()` in `app/database.py`). The DB file defaults to `./fashion.db`.

## 11. Run the FastAPI Server
```
uvicorn app.main:app --reload
```

## 12. Open the Application
Visit: http://localhost:8000
Interactive API docs (Swagger): http://localhost:8000/docs

## 13. Testing
```
pytest -q
```

## 14. Troubleshooting
- **`ModuleNotFoundError: app`** — run commands from the `python-backend/`
  folder so `app` is importable.
- **Port already in use** — `uvicorn app.main:app --reload --port 8001`.
- **Claude errors / rate limits** — the app automatically falls back to DEMO
  MODE so it keeps working.
- **CORS errors** — add your frontend origin to `CORS_ORIGINS` in `.env`.

## 15. Deployment
1. Set `ANTHROPIC_API_KEY` and a persistent `DATABASE_URL` as environment
   variables on your host.
2. Run with a production server:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   or with Gunicorn:
   ```
   gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000
   ```
3. Deploy anywhere that runs Python: Render, Railway, Fly.io, AWS, Azure, or a
   Docker container. Put a reverse proxy (nginx) in front for TLS.

---

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send a message, get a reply |
| GET | `/api/chat/{id}/messages` | Messages in a conversation |
| GET | `/api/chats` | List conversations |
| POST | `/api/chats` | Create conversation |
| DELETE | `/api/chats/{id}` | Delete conversation |
| PATCH | `/api/chats/{id}` | Rename conversation |
| POST | `/api/outfits/generate` | Generate a structured outfit |
| GET | `/api/outfits/saved` | List saved outfits |
| POST | `/api/outfits/save` | Save an outfit |
| DELETE | `/api/outfits/{id}` | Delete a saved outfit |
| PATCH | `/api/outfits/{id}` | Rename a saved outfit |
| GET/PUT | `/api/profile` | Read / update user profile |
| GET | `/api/health` | Health check |
