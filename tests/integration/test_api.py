"""
Integration tests for API endpoints.

This module contains integration tests that test the full API functionality
including database interactions and file processing.
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, get_db, Product


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_csv():
    """Create sample CSV file for testing."""
    csv_content = """name,sku,description
Test Product 1,test-001,Test description 1
Test Product 2,test-002,Test description 2
Test Product 3,test-003,Test description 3"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        f.flush()
        yield f.name
    
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


class TestProductAPI:
    """Integration tests for product API endpoints."""
    
    def test_home_page(self, client):
        """Test home page renders correctly."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_upload_non_csv_file(self, client):
        """Test uploading non-CSV file returns error."""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            f.write(b"not a csv file")
            f.seek(0)
            
            response = client.post(
                "/upload-direct",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "Only CSV files allowed" in response.json()["detail"]
    
    def test_get_status_empty_database(self, client):
        """Test status endpoint with empty database."""
        response = client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_products"] == 0
        assert data["active_products"] == 0
        assert data["inactive_products"] == 0
        assert data["database_status"] == "connected"
    
    def test_get_products_empty(self, client):
        """Test getting products from empty database."""
        response = client.get("/products")
        assert response.status_code == 200
    
    def test_delete_all_products_empty(self, client):
        """Test deleting all products from empty database."""
        response = client.delete("/products-all")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert data["deleted"] == 0


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database after each test."""
    yield
    # Clean up after test
    db = TestingSessionLocal()
    try:
        db.query(Product).delete()
        db.commit()
    finally:
        db.close()
