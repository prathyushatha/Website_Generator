
from contextlib import asynccontextmanager
from pathlib import Path
import re
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

from generator.database import (
    init_db,
    create_job,
    update_job,
    get_jobs,
    get_job,
)
from generator.website_generator import (
    analyze_reference,
    generate_website,
    make_project_name,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "generator" / "templates"
STATIC_DIR = BASE_DIR / "generator" / "static"
OUTPUT_DIR = BASE_DIR / "generated_projects"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    OUTPUT_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="AI Website Generator",
    description=(
        "Generate reusable website projects from a reference URL "
        "and written requirements."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class GenerateRequest(BaseModel):
    reference_url: str = Field(min_length=8, max_length=2048)
    requirement: str = Field(min_length=10, max_length=3000)


class AnalyzeRequest(BaseModel):
    reference_url: str = Field(min_length=8, max_length=2048)


def validate_reference_url(url: str):
    parsed = urlparse(url.strip())

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise HTTPException(
            status_code=400,
            detail="Enter a valid public HTTP or HTTPS URL.",
        )

    return url.strip()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"jobs": get_jobs()},
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "application": "AI Website Generator"}


@app.post("/api/analyze")
def analyze(payload: AnalyzeRequest):
    url = validate_reference_url(payload.reference_url)

    try:
        details = analyze_reference(url)
        return {"success": True, "reference": details}
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Reference analysis failed: {str(exc)[:300]}",
        ) from exc


@app.post("/api/generate")
def generate(payload: GenerateRequest):
    url = validate_reference_url(payload.reference_url)
    requirement = payload.requirement.strip()

    if len(requirement) < 10:
        raise HTTPException(
            status_code=400,
            detail="Please describe the website in at least 10 characters.",
        )

    project_name = make_project_name(requirement)
    job_id = create_job(url, requirement, project_name)

    try:
        reference_info = analyze_reference(url)

        project_path = generate_website(
            reference_url=url,
            requirement=requirement,
            project_name=project_name,
            reference_info=reference_info,
        )

        update_job(
            job_id,
            status="completed",
            output_path=str(project_path),
        )

        return {
            "success": True,
            "job_id": job_id,
            "project_name": project_name,
            "output_path": str(project_path),
            "preview_url": f"/preview/{project_name}",
            "run_command": (
                f"cd generated_projects\\{project_name} && "
                "python -m uvicorn main:app --reload --port 8001"
            ),
            "message": "Website project generated successfully.",
            "features": [
                "HTML homepage",
                "Contact form",
                "FastAPI backend",
                "SQLite database",
                "REST API",
                "Automated tests",
                "README instructions",
            ],
        }

    except FileExistsError as exc:
        update_job(job_id, status="failed", error_message=str(exc))
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    except Exception as exc:
        update_job(
            job_id,
            status="failed",
            error_message=str(exc)[:500],
        )
        raise HTTPException(
            status_code=400,
            detail=f"Generation failed: {str(exc)[:300]}",
        ) from exc


@app.get("/api/jobs")
def jobs():
    return {"jobs": get_jobs()}


@app.get("/api/jobs/{job_id}")
def job_details(job_id: int):
    result = get_job(job_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    return result


@app.get("/preview/{project_name}", response_class=HTMLResponse)
def preview(project_name: str):
    if not re.fullmatch(r"[a-z0-9_]{1,60}", project_name):
        raise HTTPException(status_code=400, detail="Invalid project name.")

    project_dir = (OUTPUT_DIR / project_name).resolve()

    if project_dir.parent != OUTPUT_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid project path.")

    page = project_dir / "templates" / "index.html"

    if not page.is_file():
        raise HTTPException(status_code=404, detail="Preview not found.")

    return FileResponse(page, media_type="text/html")
