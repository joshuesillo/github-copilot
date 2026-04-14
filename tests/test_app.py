import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_activity_list(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant(client):
    email = "test@student.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_invalid_activity_returns_404(client):
    response = client.post("/activities/Nonexistent/signup?email=test%40student.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_removes_participant(client):
    email = "john@mergington.edu"
    response = client.delete(f"/activities/Gym%20Class/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Gym Class"
    assert email not in activities["Gym Class"]["participants"]


def test_delete_missing_participant_returns_404(client):
    response = client.delete("/activities/Gym%20Class/participants?email=ghost%40student.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_delete_invalid_activity_returns_404(client):
    response = client.delete("/activities/Nonexistent/participants?email=test%40student.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
