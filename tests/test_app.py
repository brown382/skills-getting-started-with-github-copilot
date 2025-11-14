"""
Tests for the FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Tests for the /activities endpoint"""
    
    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@example.com",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]
    
    def test_signup_duplicate(self):
        """Test signup fails when student already signed up"""
        email = "duplicate@example.com"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}",
            follow_redirects=True
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}",
            follow_redirects=True
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_invalid_activity(self):
        """Test signup fails for non-existent activity"""
        response = client.post(
            "/activities/Non Existent Activity/signup?email=test@example.com",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregister:
    """Tests for the unregister endpoint"""
    
    def test_unregister_success(self):
        """Test successful unregistration"""
        email = "unregister@example.com"
        
        # First sign up
        client.post(
            f"/activities/Soccer Club/signup?email={email}",
            follow_redirects=True
        )
        
        # Then unregister
        response = client.post(
            f"/activities/Soccer Club/unregister?email={email}",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert email in data["message"]
    
    def test_unregister_not_signed_up(self):
        """Test unregister fails when student not signed up"""
        response = client.post(
            "/activities/Basketball Team/unregister?email=nothere@example.com",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_invalid_activity(self):
        """Test unregister fails for non-existent activity"""
        response = client.post(
            "/activities/Invalid Activity/unregister?email=test@example.com",
            follow_redirects=True
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
