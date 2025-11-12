"""
Unit tests for user routes.

Tests cover:
- User creation
- User retrieval
- User update
- User deletion
- Error handling
- Validation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Set test environment variables
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"

from app import app
from config.db import Base, get_db

# Create test database (in-memory SQLite for unit tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user data."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_user(client, test_user):
    """Test user creation."""
    response = client.post("/users/", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_user["name"]
    assert data["email"] == test_user["email"]
    assert "password" not in data  # Password should not be in response


def test_create_user_invalid_email(client, test_user):
    """Test user creation with invalid email."""
    test_user["email"] = "invalid-email"
    response = client.post("/users/", json=test_user)
    assert response.status_code == 422  # Validation error


def test_create_user_duplicate_email(client, test_user):
    """Test user creation with duplicate email."""
    # Create first user
    client.post("/users/", json=test_user)
    # Try to create second user with same email
    response = client.post("/users/", json=test_user)
    assert response.status_code == 409  # Conflict


def test_get_users(client, test_user):
    """Test getting all users."""
    # Create a user first
    client.post("/users/", json=test_user)
    # Get all users
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_user_by_id(client, test_user):
    """Test getting user by ID."""
    # Create a user first
    create_response = client.post("/users/", json=test_user)
    user_id = create_response.json()["id"]
    # Get user by ID
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["email"] == test_user["email"]


def test_get_user_not_found(client):
    """Test getting non-existent user."""
    response = client.get("/users/999")
    assert response.status_code == 404


def test_update_user(client, test_user):
    """Test user update."""
    # Create a user first
    create_response = client.post("/users/", json=test_user)
    user_id = create_response.json()["id"]
    # Update user
    updated_data = {
        "name": "Updated User",
        "email": "updated@example.com",
        "password": "newpassword123"
    }
    response = client.put(f"/users/{user_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]
    assert response.json()["email"] == updated_data["email"]


def test_delete_user(client, test_user):
    """Test user deletion."""
    # Create a user first
    create_response = client.post("/users/", json=test_user)
    user_id = create_response.json()["id"]
    # Delete user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    # Verify user is deleted
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404


def test_get_users_count(client, test_user):
    """Test getting users count."""
    # Create a few users
    for i in range(3):
        user_data = test_user.copy()
        user_data["email"] = f"test{i}@example.com"
        client.post("/users/", json=user_data)
    # Get count
    response = client.get("/users/count")
    assert response.status_code == 200
    assert response.json()["total"] >= 3

