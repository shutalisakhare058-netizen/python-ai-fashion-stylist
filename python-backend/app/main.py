from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import init_db
from app.routes import chat, conversations, outfits, users

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API routers ---
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(outfits.router)
app.include_router(users.router)


@app.get("/api/health")
def health():
    return {"ok": True, "demo_mode": settings.demo_mode}


# --- Static files & templates (frontend) ---
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "demo_mode": settings.demo_mode}
    )


@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/outfits", response_class=HTMLResponse)
def outfits_page(request: Request):
    return templates.TemplateResponse("outfits.html", {"request": request})


@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})
