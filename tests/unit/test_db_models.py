import uuid
from sqlmodel import SQLModel
from antagonist_label_store.src.backend.data_models.db import (
    Symptom, Annotator, RelevantState, Anomaly, Publisher, Service
)


def test_symptom_model():
    """Test the Symptom model."""
    symptom = Symptom(concern_score=0.8)
    assert isinstance(symptom, SQLModel)
    assert symptom.concern_score == 0.8


def test_annotator_model():
    """Test the Annotator model."""
    annotator = Annotator(
        name="Test Annotator",
        annotator_type="human", 
        version=1
    )
    assert isinstance(annotator, SQLModel)
    assert annotator.name == "Test Annotator"
    assert annotator.annotator_type == "human"
    assert annotator.version == 1


def test_relevant_state_model():
    """Test the RelevantState model."""
    relevant_state = RelevantState(
        uri="http://example.com",
        description="Test state",
        start_time="2025-09-01T12:00:00",
        end_time="2025-09-02T12:00:00",
        confidence_score=0.8,
        concern_score=0.5,
        publisher_id=uuid.uuid4(),
        service_id=uuid.uuid4()
    )
    assert isinstance(relevant_state, SQLModel)
    assert relevant_state.uri == "http://example.com"
    assert relevant_state.description == "Test state"
    assert relevant_state.start_time == "2025-09-01T12:00:00"
    assert relevant_state.end_time == "2025-09-02T12:00:00"
    assert relevant_state.confidence_score == 0.8
    assert relevant_state.concern_score == 0.5
    assert relevant_state.publisher_id is not None
    assert relevant_state.service_id is not None


def test_anomaly_model():
    """Test the Anomaly model."""
    anomaly = Anomaly(
        revision=1,
        uri="http://example.com/anomaly",
        state="confirmed",
        description="Test anomaly",
        start_time="2025-09-01T12:00:00",
        end_time="2025-09-02T12:00:00",
        confidence_score=0.9,
        pattern=None,
        annotator_id=uuid.uuid4(),
        symptom_id=uuid.uuid4()
    )
    assert isinstance(anomaly, SQLModel)
    assert anomaly.revision == 1
    assert anomaly.uri == "http://example.com/anomaly"
    assert anomaly.state == "confirmed"
    assert anomaly.description == "Test anomaly"
    assert anomaly.start_time == "2025-09-01T12:00:00"
    assert anomaly.end_time == "2025-09-02T12:00:00"
    assert anomaly.confidence_score == 0.9
    assert anomaly.pattern is None
    assert anomaly.annotator_id is not None
    assert anomaly.symptom_id is not None


def test_publisher_model():
    """Test the Publisher model."""
    publisher = Publisher(
        name="Test Publisher",
        version="1.0"
    )
    assert isinstance(publisher, SQLModel)
    assert publisher.name == "Test Publisher"
    assert publisher.version == "1.0"


def test_service_model():
    """Test the Service model."""
    service = Service(
        id=uuid.uuid4(),
        name="Test Service",
        description="Test service description"
    )
    assert isinstance(service, SQLModel)
    assert service.id is not None
