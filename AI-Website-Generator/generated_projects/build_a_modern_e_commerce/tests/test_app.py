
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
