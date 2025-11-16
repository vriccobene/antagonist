import sys
from pathlib import Path
from fastapi.testclient import TestClient
from antagonist_label_store.src.backend.main import app
from antagonist_label_store.src.backend.db.database import engine

# Add the backend directory to the Python path
sys.path.append(
    str(
        Path(__file__).resolve().parent.parent.parent
        / "antagonist_label_store"
        / "src"
    )
)


def test_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Antagonist API", "version": "0.1.0"}


def test_database_connection():
    """Test if the database connection can be established."""
    with engine.connect() as connection:
        assert connection.closed is False
