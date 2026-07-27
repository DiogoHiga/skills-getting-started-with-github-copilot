import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_all_activities():
    # Arrange
    with TestClient(app) as client:
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert "Chess Club" in body
        assert body["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert isinstance(body["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
        assert email in activities[activity_name]["participants"]


def test_signup_returns_400_for_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Removed {email} from {activity_name}"}
        assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
