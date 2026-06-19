"""
Backend API tests for the Mergington High School Activities API.
Uses the AAA (Arrange-Act-Assert) pattern throughout.
"""


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_all_activities(client):
    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert — all 9 seeded activities are present
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club",
    ]
    for activity in expected_activities:
        assert activity in data


def test_get_activities_payload_shape(client):
    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert — each activity has the expected fields
    for name, details in data.items():
        assert "description" in details, f"{name} missing 'description'"
        assert "schedule" in details, f"{name} missing 'schedule'"
        assert "max_participants" in details, f"{name} missing 'max_participants'"
        assert "participants" in details, f"{name} missing 'participants'"
        assert isinstance(details["participants"], list), f"{name} participants should be a list"


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert activity in response.json()["message"]


def test_signup_duplicate_returns_400(client):
    # Arrange — michael is already in Chess Club from seed data
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_is_immediately_visible_in_get(client):
    # Arrange
    activity = "Tennis Club"
    email = "newplayer@mergington.edu"

    # Act
    client.post(f"/activities/{activity}/signup?email={email}")
    response = client.get("/activities")

    # Assert — new participant appears in the activity's list
    data = response.json()
    assert email in data[activity]["participants"]


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange — ava is already in Tennis Club from seed data
    activity = "Tennis Club"
    email = "ava@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert activity in response.json()["message"]


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    activity = "Tennis Club"
    email = "ava@mergington.edu"

    # Act
    client.delete(f"/activities/{activity}/signup?email={email}")
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert email not in data[activity]["participants"]


def test_unregister_non_member_returns_404(client):
    # Arrange
    activity = "Chess Club"
    email = "notamember@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
