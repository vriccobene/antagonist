from fastapi.testclient import TestClient
from antagonist_label_store.src.backend.main import app
from antagonist_label_store.src.backend.db.database import engine
from sqlalchemy.orm import sessionmaker
from antagonist_label_store.src.backend.data_models.db import (
    Symptom, Annotator, RelevantState, Anomaly, Publisher, Service
)
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(
    str(
        Path(__file__).resolve().parent.parent.parent
        / "antagonist_label_store"
        / "src"
    )
)

# Create a test client
client = TestClient(app)

# Create a session for direct database interaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_end_to_end_symptom():
    """Test end-to-end creation and retrieval of a Symptom."""
    symptom_data = {
        "concern_score": 0.8,
        "description": "Test Symptom",
        "severity": "high"
    }
    response = client.post("/symptoms/", json=symptom_data)
    assert response.status_code == 201
    created_symptom = response.json()

    with SessionLocal() as session:
        db_symptom = session.query(Symptom).filter_by(
            id=created_symptom["id"]
        ).first()
        assert db_symptom is not None
        assert db_symptom.concern_score == symptom_data["concern_score"]
        assert db_symptom.description == symptom_data["description"]
        assert db_symptom.severity == symptom_data["severity"]

    get_response = client.get(f"/symptoms/{created_symptom['id']}")
    assert get_response.status_code == 200
    retrieved_symptom = get_response.json()
    assert retrieved_symptom == created_symptom


def test_end_to_end_annotator():
    """Test end-to-end creation and retrieval of an Annotator."""
    annotator_data = {
        "name": "Test Annotator",
        "annotator_type": "human",
        "description": "Test Annotator Description",
        "experience_level": "expert"
    }
    response = client.post("/annotators/", json=annotator_data)
    assert response.status_code == 201
    created_annotator = response.json()

    with SessionLocal() as session:
        db_annotator = session.query(Annotator).filter_by(
            id=created_annotator["id"]
        ).first()
        assert db_annotator is not None
        assert db_annotator.name == annotator_data["name"]
        assert db_annotator.annotator_type == annotator_data["annotator_type"]
        assert db_annotator.description == annotator_data["description"]
        assert db_annotator.experience_level == annotator_data[
            "experience_level"
        ]

    get_response = client.get(f"/annotators/{created_annotator['id']}")
    assert get_response.status_code == 200
    retrieved_annotator = get_response.json()
    assert retrieved_annotator == created_annotator


def test_end_to_end_relevant_state():
    """Test end-to-end creation and retrieval of a RelevantState."""
    relevant_state_data = {
        "uri": "http://example.com",
        "description": "Test Relevant State",
        "concern_score": 0.5,
        "state_type": "Test Type",
        "priority": "medium"
    }
    response = client.post("/relevant_states/", json=relevant_state_data)
    assert response.status_code == 201
    created_relevant_state = response.json()

    with SessionLocal() as session:
        db_relevant_state = session.query(RelevantState).filter_by(
            id=created_relevant_state["id"]
        ).first()
        assert db_relevant_state is not None
        assert db_relevant_state.uri == relevant_state_data["uri"]
        assert db_relevant_state.description == relevant_state_data[
            "description"
        ]
        assert db_relevant_state.concern_score == relevant_state_data[
            "concern_score"
        ]
        assert db_relevant_state.state_type == relevant_state_data[
            "state_type"
        ]
        assert db_relevant_state.priority == relevant_state_data["priority"]

    get_response = client.get(
        f"/relevant_states/{created_relevant_state['id']}"
    )
    assert get_response.status_code == 200
    retrieved_relevant_state = get_response.json()
    assert retrieved_relevant_state == created_relevant_state


def test_end_to_end_anomaly():
    """Test end-to-end creation and retrieval of an Anomaly."""
    anomaly_data = {
        "state": "confirmed",
        "confidence_score": 0.9,
        "description": "Test Anomaly",
        "impact": "critical"
    }
    response = client.post("/anomalies/", json=anomaly_data)
    assert response.status_code == 201
    created_anomaly = response.json()

    with SessionLocal() as session:
        db_anomaly = session.query(Anomaly).filter_by(
            id=created_anomaly["id"]
        ).first()
        assert db_anomaly is not None
        assert db_anomaly.state == anomaly_data["state"]
        assert db_anomaly.confidence_score == anomaly_data["confidence_score"]
        assert db_anomaly.description == anomaly_data["description"]
        assert db_anomaly.impact == anomaly_data["impact"]

    get_response = client.get(f"/anomalies/{created_anomaly['id']}")
    assert get_response.status_code == 200
    retrieved_anomaly = get_response.json()
    assert retrieved_anomaly == created_anomaly


def test_end_to_end_publisher():
    """Test end-to-end creation and retrieval of a Publisher."""
    publisher_data = {
        "name": "Test Publisher",
        "description": "Test Publisher Description",
        "region": "North America"
    }
    response = client.post("/publishers/", json=publisher_data)
    assert response.status_code == 201
    created_publisher = response.json()

    with SessionLocal() as session:
        db_publisher = session.query(Publisher).filter_by(
            id=created_publisher["id"]
        ).first()
        assert db_publisher is not None
        assert db_publisher.name == publisher_data["name"]
        assert db_publisher.description == publisher_data["description"]
        assert db_publisher.region == publisher_data["region"]

    get_response = client.get(f"/publishers/{created_publisher['id']}")
    assert get_response.status_code == 200
    retrieved_publisher = get_response.json()
    assert retrieved_publisher == created_publisher


def test_end_to_end_service():
    """Test end-to-end creation and retrieval of a Service."""
    service_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Service",
        "description": "Test Service Description",
        "availability": "24/7"
    }
    response = client.post("/services/", json=service_data)
    assert response.status_code == 201
    created_service = response.json()

    with SessionLocal() as session:
        db_service = session.query(Service).filter_by(
            id=created_service["id"]
        ).first()
        assert db_service is not None
        assert db_service.name == service_data["name"]
        assert db_service.description == service_data["description"]
        assert db_service.availability == service_data["availability"]

    get_response = client.get(f"/services/{created_service['id']}")
    assert get_response.status_code == 200
    retrieved_service = get_response.json()
    assert retrieved_service == created_service
