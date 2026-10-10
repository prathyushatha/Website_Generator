
import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "generated_projects"


def make_project_name(requirement: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", requirement.lower())
    name = "_".join(words[:5])
    return name or "generated_website"


def detect_website_type(requirement: str) -> str:
    """Detect the most likely website category from the request."""
    text = requirement.lower()

    categories = {
        "ecommerce": [
            "e-commerce", "ecommerce", "online store",
            "shopping cart", "product listing", "checkout",
            "buy products", "sell products",
        ],
        "portfolio": [
            "portfolio", "personal website", "personal brand",
            "developer portfolio", "photography portfolio",
        ],
        "education": [
            "school", "college", "student management",
            "learning management", "online course",
            "education", "e-learning", "university",
        ],
        "dashboard": [
            "dashboard", "admin panel", "management system",
            "analytics dashboard", "business intelligence",
        ],
        "restaurant": [
            "restaurant", "food ordering", "food delivery",
            "menu website", "cafe website", "café website",
        ],
    }

    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "business"


def analyze_reference(reference_url: str) -> dict:
    """Read basic public HTML information without requiring an AI key."""
    import requests
    from bs4 import BeautifulSoup

    parsed = urlparse(reference_url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS reference URL.")

    if parsed.username or parsed.password:
        raise ValueError(
            "URLs containing embedded credentials are not supported."
        )

    response = requests.get(
        reference_url,
        timeout=8,
        headers={"User-Agent": "AIWebsiteGenerator/1.0"},
        allow_redirects=False,
    )
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type.lower():
        raise ValueError("The reference URL must return an HTML page.")

    soup = BeautifulSoup(response.text, "html.parser")

    title = (
        soup.title.get_text(" ", strip=True)
        if soup.title
        else parsed.hostname
    )

    headings = [
        heading.get_text(" ", strip=True)
        for heading in soup.find_all(["h1", "h2", "h3"])[:12]
    ]

    links = []
    for link in soup.find_all("a", href=True)[:20]:
        text = link.get_text(" ", strip=True)
        if text:
            links.append(text[:100])

    return {
        "url": reference_url,
        "title": title[:200],
        "headings": headings,
        "links": links,
    }


def get_category_content(website_type: str) -> dict:
    """Return category-specific homepage sections and navigation."""

    content = {
        "ecommerce": {
            "nav": [("Products", "#products"), ("About", "#about"),
                    ("Contact", "#contact")],
            "heading": "Discover Products You'll Love",
            "intro": (
                "Explore our featured collection and discover "
                "products selected for quality, value, and style."
            ),
            "section_title": "Featured Products",
            "section_intro": (
                "Sample product cards are provided as a starting point "
                "for your own product catalogue."
            ),
            "cards": [
                ("Product One", "A versatile product for everyday use."),
                ("Product Two", "A thoughtful design with useful features."),
                ("Product Three", "A popular choice for your collection."),
            ],
            "card_label": "Sample product",
            "cta": "Explore Products",
            "target": "#products",
        },
        "portfolio": {
            "nav": [("Projects", "#projects"), ("About", "#about"),
                    ("Contact", "#contact")],
            "heading": "Ideas Into Impactful Work",
            "intro": (
                "A personal portfolio to showcase skills, projects, "
                "experience, and the work you are proud to share."
            ),
            "section_title": "Featured Projects",
            "section_intro": (
                "Replace these example projects with your own work, "
                "technologies, achievements, and project links."
            ),
            "cards": [
                ("Project One", "Describe a project and the problem it solves."),
                ("Project Two", "Highlight the tools and skills you used."),
                ("Project Three", "Showcase an outcome or key achievement."),
            ],
            "card_label": "Portfolio project",
            "cta": "View Projects",
            "target": "#projects",
        },
        "education": {
            "nav": [("Programs", "#programs"), ("About", "#about"),
                    ("Contact", "#contact")],
            "heading": "Learn, Grow, and Achieve More",
            "intro": (
                "Explore learning programs and educational resources "
                "designed to help students develop new skills."
            ),
            "section_title": "Learning Programs",
            "section_intro": (
                "These sample programs are placeholders. Add your real "
                "courses, lessons, instructors, and enrolment workflow."
            ),
            "cards": [
                ("Programming", "Build a foundation in coding and problem solving."),
                ("Data Science", "Explore data analysis and machine learning."),
                ("Web Development", "Learn the building blocks of modern websites."),
            ],
            "card_label": "Sample program",
            "cta": "Explore Programs",
            "target": "#programs",
        },
        "dashboard": {
            "nav": [("Overview", "#overview"), ("About", "#about"),
                    ("Contact", "#contact")],
            "heading": "Your Information, Clearly Presented",
            "intro": (
                "A dashboard-style starter with overview cards and a "
                "structured layout for your management application."
            ),
            "section_title": "Overview",
            "section_intro": (
                "The figures below are demonstration values, not live "
                "business data. Connect them to your database or APIs."
            ),
            "cards": [
                ("Total Records", "1,250 sample records"),
                ("Active Items", "86 sample active items"),
                ("Pending Tasks", "14 sample pending tasks"),
            ],
            "card_label": "Demo metric",
            "cta": "Contact Us",
            "target": "#contact",
        },
        "restaurant": {
            "nav": [("Menu", "#menu"), ("About", "#about"),
                    ("Contact", "#contact")],
            "heading": "Fresh Flavours, Memorable Moments",
            "intro": (
                "Discover our sample menu and get in touch to ask about "
                "dining, catering, or food services."
            ),
            "section_title": "Popular Menu Items",
            "section_intro": (
                "Update these sample menu items and descriptions to "
                "match your restaurant's actual menu."
            ),
            "cards": [
                ("Signature Starter", "A delicious way to begin your meal."),
                ("House Special", "A featured dish made for food lovers."),
                ("Sweet Finish", "A dessert to complete the experience."),
            ],
            "card_label": "Sample menu item",
            "cta": "Explore Menu",
            "target": "#menu",
        },
        "business": {
            "nav": [("Services", "#services"), ("About", "#about"),
                    ("Contact", "#contact")],
            "heading": "Solutions Designed Around Your Goals",
            "intro": (
                "A modern business website starter to present your services, "
                "share your value, and help customers contact you."
            ),
            "section_title": "Our Services",
            "section_intro": (
                "Customize these service cards to describe your real "
                "business offerings."
            ),
            "cards": [
                ("Consulting", "Practical guidance tailored to your goals."),
                ("Digital Solutions", "Technology to support your business."),
                ("Customer Support", "Helpful service throughout your journey."),
            ],
            "card_label": "Service",
            "cta": "Explore Services",
            "target": "#services",
        },
    }

    return content.get(website_type, content["business"])


def generate_website(
    reference_url: str,
    requirement: str,
    project_name: str | None = None,
    reference_info: dict | None = None,
) -> Path:
    if not requirement or not requirement.strip():
        raise ValueError("Website requirements cannot be empty.")

    website_type = detect_website_type(requirement)
    project_name = project_name or make_project_name(requirement)

    if not re.fullmatch(r"[a-z0-9_]{1,60}", project_name):
        raise ValueError("Invalid project name.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project_dir = OUTPUT_DIR / project_name

    if project_dir.exists():
        raise FileExistsError(
            f"The project '{project_name}' already exists. "
            "Use a different requirement or project name."
        )

    site_title = escape(project_name.replace("_", " ").title())
    safe_requirement = escape(requirement.strip())
    safe_reference = escape(reference_url, quote=True)

    reference_title = "Your New Website"
    if reference_info:
        reference_title = escape(
            str(reference_info.get("title", "Your New Website"))[:200]
        )

    category = get_category_content(website_type)

    nav_html = "\n".join(
        f'<a href="{escape(target, quote=True)}">'
        f'{escape(label)}</a>'
        for label, target in category["nav"]
    )

    cards_html = "\n".join(
        f"""
        <article class="feature-card">
          <span class="eyebrow">{escape(category["card_label"])}</span>
          <h3>{escape(title)}</h3>
          <p>{escape(description)}</p>
        </article>
        """
        for title, description in category["cards"]
    )

    section_id = {
        "ecommerce": "products",
        "portfolio": "projects",
        "education": "programs",
        "dashboard": "overview",
        "restaurant": "menu",
        "business": "services",
    }.get(website_type, "services")

    templates_dir = project_dir / "templates"
    tests_dir = project_dir / "tests"
    templates_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)

    files = {
        "requirements.txt": """fastapi
uvicorn
jinja2
python-multipart
pytest
httpx
""",
        "main.py": r'''
import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
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
''',
        "templates/index.html": f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{safe_requirement[:250]}">
<title>{site_title}</title>
<style>
:root {{
  color-scheme: light;
  --primary: #4f46e5;
  --dark: #111827;
  --text: #172033;
  --muted: #64748b;
  --surface: #ffffff;
  --border: #e5e7eb;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  font-family: Inter, Arial, sans-serif;
  color: var(--text);
  background: #f5f7fb;
  line-height: 1.65;
}}
header {{
  background: var(--dark);
  color: white;
  padding: 18px 7%;
}}
nav {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}}
nav strong {{ font-size: 1.15rem; }}
nav a {{
  color: white;
  text-decoration: none;
  margin-left: 18px;
}}
nav a:hover {{ text-decoration: underline; }}
.hero {{
  padding: 88px 7%;
  text-align: center;
  background: linear-gradient(125deg, #e0e7ff, #ffffff 65%, #fce7f3);
}}
.hero-inner {{ max-width: 850px; margin: 0 auto; }}
.eyebrow {{
  display: inline-block;
  color: var(--primary);
  font-size: .82rem;
  font-weight: 700;
  letter-spacing: .07em;
  text-transform: uppercase;
}}
.hero h1 {{
  font-size: clamp(2.2rem, 6vw, 4.2rem);
  line-height: 1.12;
  letter-spacing: -.04em;
  margin: 14px 0;
}}
.hero p {{ max-width: 720px; margin: 16px auto 24px; }}
.button {{
  display: inline-block;
  background: var(--primary);
  color: white;
  padding: 12px 22px;
  border: 0;
  border-radius: 9px;
  text-decoration: none;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}}
.button:hover {{ filter: brightness(.92); }}
section {{ padding: 58px 7%; scroll-margin-top: 20px; }}
.section-heading {{
  max-width: 760px;
  margin: 0 auto 28px;
  text-align: center;
}}
.section-heading h2 {{ font-size: clamp(1.7rem, 4vw, 2.5rem); margin: 8px 0; }}
.grid {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  max-width: 1100px;
  margin: 0 auto;
}}
.feature-card, .panel {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(15, 23, 42, .04);
}}
.feature-card h3 {{ margin-bottom: 8px; }}
.feature-card p, .muted {{ color: var(--muted); }}
.panel {{ max-width: 820px; margin: 0 auto; }}
.panel a {{ overflow-wrap: anywhere; }}
form {{ margin-top: 20px; }}
label {{ display: block; margin-top: 14px; font-weight: 700; }}
input, textarea {{
  width: 100%;
  padding: 12px;
  margin-top: 6px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font: inherit;
}}
textarea {{ min-height: 120px; resize: vertical; }}
#status {{ margin-top: 12px; }}
footer {{
  text-align: center;
  padding: 26px 7%;
  color: var(--muted);
  background: white;
}}
@media (max-width: 760px) {{
  .grid {{ grid-template-columns: 1fr; }}
  .hero {{ padding-top: 62px; padding-bottom: 62px; }}
  nav {{ align-items: flex-start; }}
  nav div {{ display: flex; flex-wrap: wrap; gap: 12px; }}
  nav a {{ margin-left: 0; }}
}}
</style>
</head>
<body>
<header>
  <nav aria-label="Main navigation">
    <strong>{site_title}</strong>
    <div>{nav_html}<a href="#contact">Contact</a></div>
  </nav>
</header>

<main>
  <section class="hero">
    <div class="hero-inner">
      <span class="eyebrow">{escape(website_type.title())} Website</span>
      <h1>{escape(category["heading"])}</h1>
      <p>{escape(category["intro"])}</p>
      <p>{safe_requirement}</p>
      <a class="button" href="{escape(category["target"], quote=True)}">
        {escape(category["cta"])}
      </a>
    </div>
  </section>

  <section id="{section_id}">
    <div class="section-heading">
      <span class="eyebrow">{escape(category["card_label"])}</span>
      <h2>{escape(category["section_title"])}</h2>
      <p class="muted">{escape(category["section_intro"])}</p>
    </div>
    <div class="grid">
      {cards_html}
    </div>
  </section>

  <section id="about">
    <div class="panel">
      <span class="eyebrow">About</span>
      <h2>Welcome to {site_title}</h2>
      <p>This website was generated by AI Website Generator based on
      the submitted requirements.</p>
      <p><strong>Reference website:</strong>
      <a href="{safe_reference}" target="_blank"
         rel="noopener noreferrer">{safe_reference}</a></p>
      <p class="muted">Use this starter to develop and customize your
      website further.</p>
    </div>
  </section>

  <section id="contact">
    <div class="panel">
      <span class="eyebrow">Get in touch</span>
      <h2>Contact Us</h2>
      <p class="muted">Submit a message using the form below. The
      backend saves contact messages to the local SQLite database.</p>
      <form id="contact-form">
        <label for="name">Name</label>
        <input id="name" name="name" maxlength="100" required>

        <label for="email">Email</label>
        <input id="email" name="email" type="email"
               maxlength="254" required>

        <label for="message">Message</label>
        <textarea id="message" name="message"
                  maxlength="5000" required></textarea>

        <p><button class="button" type="submit">Send Message</button></p>
        <p id="status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </section>
</main>

<footer>Generated locally · {site_title}</footer>

<script>
document.getElementById("contact-form").addEventListener(
  "submit",
  async function(event) {{
    event.preventDefault();

    const form = event.currentTarget;
    const status = document.getElementById("status");
    const button = form.querySelector('button[type="submit"]');

    status.textContent = "Sending...";
    button.disabled = true;

    try {{
      const response = await fetch("/api/contact", {{
        method: "POST",
        body: new FormData(form)
      }});

      const data = await response.json();

      if (!response.ok) {{
        const detail = Array.isArray(data.detail)
          ? data.detail.map(item => item.msg).join(", ")
          : data.detail;
        throw new Error(detail || "Request failed");
      }}

      status.textContent = "Message saved successfully.";
      form.reset();
    }} catch (error) {{
      status.textContent = "Could not send message: " + error.message;
    }} finally {{
      button.disabled = false;
    }}
  }}
);
</script>
</body>
</html>
''',
        "tests/test_app.py": r'''
from fastapi.testclient import TestClient
from main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_home_page():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "Contact Us" in response.text


def test_contact_validation():
    with TestClient(app) as client:
        response = client.post(
            "/api/contact",
            data={"name": "", "email": "", "message": ""},
        )
        assert response.status_code == 422


def test_contact_submission():
    with TestClient(app) as client:
        response = client.post(
            "/api/contact",
            data={
                "name": "Generator Test",
                "email": "test@example.com",
                "message": "Test contact submission",
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
''',
        "README.md": f"""# {project_name}

A website generated by AI Website Generator.

## Website category

{website_type}

## Requirements

Python 3.10 or newer.

## Run locally on Windows

```bat
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001

API documentation: http://127.0.0.1:8001/docs

Health check: http://127.0.0.1:8001/api/health

## Run tests

```bat
python -m pytest -q
```

## Original request

{requirement}

## Reference URL

{reference_url}

## Notes

The category cards contain sample content. Features such as real product
purchasing, user authentication, live analytics, course enrolment, and
online payments need their own implementation and configuration.
""",
        "project.json": json.dumps(
            {
                "name": project_name,
                "website_type": website_type,
                "reference_url": reference_url,
                "requirement": requirement,
                "reference_info": reference_info or {},
                "features": [
                    "responsive_homepage",
                    "category_specific_sections",
                    "contact_form",
                    "sqlite",
                    "rest_api",
                    "automated_tests",
                ],
            },
            indent=2,
        ),
    }

    try:
        for relative_path, content in files.items():
            destination = project_dir / relative_path
            destination.write_text(content, encoding="utf-8")

        return project_dir

    except Exception:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise