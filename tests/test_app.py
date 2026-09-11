class TestRootEndpoint:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivitiesEndpoint:
    def test_get_activities_returns_activity_data(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert expected_activity in response.json()
        assert {
            "description",
            "schedule",
            "max_participants",
            "participants",
        } <= response.json()[expected_activity].keys()


class TestSignupEndpoint:
    def test_signup_adds_participant(self, client, activity_data):
        # Arrange
        activity = "Chess Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in activity_data[activity]["participants"]
        assert response.json() == {
            "message": f"Signed up {email} for {activity}"
        }

    def test_signup_rejects_unknown_activity(self, client):
        # Arrange
        activity = "Unknown Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_rejects_duplicate_participant(self, client, activity_data):
        # Arrange
        activity = "Chess Club"
        email = activity_data[activity]["participants"][0]
        participant_count = activity_data[activity]["participants"].count(email)

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Student already signed up for this activity"
        )
        assert activity_data[activity]["participants"].count(email) == participant_count

    def test_participant_can_signup_for_different_activity(
        self, client, activity_data
    ):
        # Arrange
        email = activity_data["Chess Club"]["participants"][0]
        activity = "Programming Class"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in activity_data[activity]["participants"]


class TestUnregisterEndpoint:
    def test_unregister_removes_participant(self, client, activity_data):
        # Arrange
        activity = "Chess Club"
        email = activity_data[activity]["participants"][0]

        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email}",
        )

        # Assert
        assert response.status_code == 200
        assert email not in activity_data[activity]["participants"]
        assert response.json() == {
            "message": f"Unregistered {email} from {activity}"
        }

    def test_unregister_rejects_unknown_activity(self, client):
        # Arrange
        activity = "Unknown Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email}",
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_rejects_missing_participant(self, client, activity_data):
        # Arrange
        activity = "Chess Club"
        email = "not.registered@mergington.edu"
        original_participants = activity_data[activity]["participants"].copy()

        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email}",
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Student is not signed up for this activity"
        )
        assert activity_data[activity]["participants"] == original_participants

    def test_unregistered_participant_can_signup_again(self, client, activity_data):
        # Arrange
        activity = "Chess Club"
        email = activity_data[activity]["participants"][0]

        # Act
        unregister_response = client.delete(
            f"/activities/{activity}/participants/{email}",
        )
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        assert email in activity_data[activity]["participants"]
