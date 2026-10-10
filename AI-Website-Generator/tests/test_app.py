
from fastapi.testclient import TestClient

from generator.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_dashboard_loads():
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert "AI Website Generator" in response.text
        assert "Generate Website" in response.text


def test_generate_rejects_invalid_url():
    with TestClient(app) as client:
        response = client.post(
            "/api/generate",
            json={
                "reference_url": "not-a-valid-url",
                "requirement": (
                    "Create a business website with a contact form."
                ),
            },
        )

        assert response.status_code == 400


def test_generate_rejects_short_requirement():
    with TestClient(app) as client:
        response = client.post(
            "/api/generate",
            json={
                "reference_url": "https://example.com",
                "requirement": "Short",
            },
        )

        assert response.status_code == 422


def test_jobs_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/jobs")

        assert response.status_code == 200
        assert "jobs" in response.json()