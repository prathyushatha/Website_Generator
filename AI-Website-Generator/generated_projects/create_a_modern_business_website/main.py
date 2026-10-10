
import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "website.db"
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Generated Website API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.post("/api/contact")
def create_contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
):
    name = name.strip()
    email = email.strip()
    message = message.strip()

    if not name or not email or not message:
        raise HTTPException(400, "All fields are required.")

    if len(name) > 100 or len(email) > 254 or len(message) > 5000:
        raise HTTPException(400, "One or more fields are too long.")

    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute(
            "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
            (name, email, message),
        )
        contact_id = cursor.lastrowid

    return {"success": True, "contact_id": contact_id}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/contacts")
def list_contacts():
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            "SELECT id, name, email, message, created_at "
            "FROM contacts ORDER BY id DESC LIMIT 100"
        ).fetchall()

    return {"contacts": [dict(row) for row in rows]}
