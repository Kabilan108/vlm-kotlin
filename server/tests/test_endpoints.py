from fastapi.testclient import TestClient
import pytest

from app.main import app, admin_only

client = TestClient(app)


def test_create_ocr_job():
    # Create a sample image file
    with open("data/doctors-note.jpg", "rb") as f:
        response = client.post(
            "/ocr", files={"file": ("doctors-note.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    assert "job_id" in response.json()


def test_get_ocr_job():
    # First, create a job
    with open("data/doctors-note.jpg", "rb") as f:
        response = client.post(
            "/ocr", files={"file": ("doctors-note.jpg", f, "image/jpeg")}
        )

    job_id = response.json()["job_id"]

    # Now, get the job status
    response = client.get(f"/ocr/{job_id}")
    assert response.status_code == 200
    assert "status" in response.json()


def test_get_nonexistent_job():
    response = client.get("/ocr/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.parametrize("admin", [True, False])
def test_admin_jobs(admin):
    # Mock the admin_only dependency
    app.dependency_overrides[admin_only] = lambda: admin

    response = client.get("/admin/jobs")

    if admin:
        assert response.status_code == 200
        assert "total_jobs" in response.json()
    else:
        assert response.status_code == 403, response.text

    # Clear the override after the test
    app.dependency_overrides.clear()
