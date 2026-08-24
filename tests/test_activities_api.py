import pytest


def test_get_activities_returns_expected_structure(client):
    # Arrange
    expected_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload

    for activity in payload.values():
        assert expected_fields.issubset(activity.keys())
        assert isinstance(activity["participants"], list)


def test_signup_adds_participant_when_activity_exists(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities")
    activities_payload = activities_response.json()
    assert email in activities_payload[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Student already signed up for this activity"


def test_signup_returns_422_when_email_is_missing(client):
    # Arrange
    activity_name = "Soccer Team"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant_when_present(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    activities_payload = activities_response.json()
    assert email not in activities_payload[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_unregister_returns_404_for_missing_participant(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "not.enrolled@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Participant not found in this activity"


def test_unregister_returns_422_when_email_is_missing(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants")

    # Assert
    assert response.status_code == 422


@pytest.mark.parametrize("run", [1, 2])
def test_state_isolated_between_test_runs(client, run):
    # Arrange
    activity_name = "Soccer Team"
    email = "isolated.student@mergington.edu"

    # Act
    before_response = client.get("/activities")
    before_payload = before_response.json()
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    after_response = client.get("/activities")
    after_payload = after_response.json()

    # Assert
    assert email not in before_payload[activity_name]["participants"]
    assert signup_response.status_code == 200
    assert email in after_payload[activity_name]["participants"]
