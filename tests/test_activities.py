import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_redirect(self, client: TestClient):
        """Test that root endpoint redirects to static index."""
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_success(self, client: TestClient, sample_activities):
        """Test successful retrieval of all activities."""
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == expected_activity_count

        # Check that all expected activities are present
        expected_activities = set(sample_activities.keys())
        actual_activities = set(data.keys())
        assert expected_activities == actual_activities

    def test_activity_structure(self, client: TestClient):
        """Test that each activity has the correct structure."""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data

            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

            # Participants should be list of strings (emails)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client: TestClient):
        """Test successful signup."""
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_updates_participants(self, client: TestClient):
        """Test that signup actually adds participant to the list."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Get initial count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        response = client.get("/activities")
        updated_data = response.json()
        updated_count = len(updated_data[activity_name]["participants"])

        assert updated_count == initial_count + 1
        assert email in updated_data[activity_name]["participants"]

    def test_signup_activity_not_found(self, client: TestClient):
        """Test signup with non-existent activity."""
        # Arrange
        invalid_activity = "NonExistent"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client: TestClient):
        """Test signup when participant is already enrolled."""
        # Arrange
        activity_name = "Programming Class"
        email = "duplicate@mergington.edu"

        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Second signup with same email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_activity_full(self, client: TestClient):
        """Test signup when activity reaches capacity."""
        # Arrange
        activity_name = "Tennis Club"  # Max 16, currently has 2

        # Fill up the activity
        for i in range(14):  # Add 14 more to reach capacity
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@mergington.edu"}
            )

        # Act - Try to add one more
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "laststudent@mergington.edu"}
        )

        # Assert
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "full" in data["detail"]


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client: TestClient):
        """Test successful unregister."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_updates_participants(self, client: TestClient):
        """Test that unregister actually removes participant from the list."""
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"

        # Get initial count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity_name]["participants"])

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        response = client.get("/activities")
        updated_data = response.json()
        updated_count = len(updated_data[activity_name]["participants"])

        assert updated_count == initial_count - 1
        assert email not in updated_data[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client: TestClient):
        """Test unregister with non-existent activity."""
        # Arrange
        invalid_activity = "NonExistent"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_enrolled(self, client: TestClient):
        """Test unregister when participant is not enrolled."""
        # Arrange
        activity_name = "Chess Club"
        email = "notenrolled@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple operations."""

    def test_signup_then_unregister_workflow(self, client: TestClient):
        """Test complete signup and unregister workflow."""
        # Arrange
        email = "workflowtest@mergington.edu"
        activity = "Programming Class"

        # Act - Sign up
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert signup
        assert signup_response.status_code == 200

        # Verify enrolled
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]

        # Act - Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

        # Assert unregister
        assert unregister_response.status_code == 200

        # Verify unenrolled
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]

    def test_capacity_edge_cases(self, client: TestClient):
        """Test edge cases around activity capacity."""
        # Arrange
        activity = "Debate Team"  # Max 18, currently has 1

        # Act - Fill to capacity
        for i in range(17):  # Add 17 more (1 already exists)
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": f"capacity{i}@mergington.edu"}
            )
            assert response.status_code == 200

        # Assert at capacity
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity]["participants"]) == 18

        # Act - Try to exceed capacity
        over_capacity_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": "overcapacity@mergington.edu"}
        )

        # Assert capacity exceeded
        assert over_capacity_response.status_code == 400

        # Act - Unregister one participant
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": "capacity0@mergington.edu"}
        )

        # Act - Now should be able to add one more
        final_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": "newcapacity@mergington.edu"}
        )

        # Assert final signup succeeds
        assert final_response.status_code == 200