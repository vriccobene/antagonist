import uuid
from pydantic import PastDatetime
from typing import Optional, List
from sqlmodel import (
    Field, Relationship, SQLModel,
    UniqueConstraint, DateTime, PrimaryKeyConstraint)
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB
from data_models.label_store import api
from .common import AnnotatorType, AnomalyPattern, State


class Symptom(SQLModel, table=True):
    __table_args__ = {
        "extend_existing": True
    }  # Allow redefinition of the table
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True,
        description=(
            "Unique identifier for the symptom. "
            "If the symptom has been created, "
            "this field is populated automatically, "
            "so it is not mandatory"
        )
    )
    concern_score: float = Field(ge=0.0, le=1.0)
    metric: Optional[str] = Field(default="")
    dimensions: Optional[dict] = Field(
        default=None, sa_column_kwargs={"nullable": True}, sa_type=JSONB
    )
    data: Optional[dict] = Field(
        default=None, sa_column_kwargs={"nullable": True}, sa_type=JSONB
    )


class Annotator(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name", "version", "annotator_type",
            name="annotator_version"),
        {"extend_existing": True}
    )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True)
    name: str
    version: Optional[int] = Field(default=0)
    annotator_type: AnnotatorType


class RelevantStateAnomalyLink(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint(
            "relevant_state_id",
            "anomaly_id",
            name="relevantstate_anomaly_link"
        ),
        UniqueConstraint(
            "relevant_state_id",
            "anomaly_id",
            name="relevantstate_anomaly_link"
        ),
        ForeignKeyConstraint(
            ["relevant_state_id"],
            ["relevantstate.id"]
        ),
        {"extend_existing": True}
    )
    relevant_state_id: Optional[uuid.UUID] = Field(default=None)
    anomaly_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="anomaly.id"
    )


class HistoricalRelevantStateAnomalyLink(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint(
            "historical_relevant_state_id",
            "historical_relevant_state_revision",
            "anomaly_id",
            name="historical_relevantstate_anomaly_revision_link"
        ),
        UniqueConstraint(
            "historical_relevant_state_id",
            "historical_relevant_state_revision",
            "anomaly_id",
            name="historical_relevantstate_anomaly_revision_link"
        ),
        ForeignKeyConstraint(
            ["historical_relevant_state_id",
             "historical_relevant_state_revision"],
            ["historicalrelevantstate.id",
             "historicalrelevantstate.revision"]
        ),
        {"extend_existing": True}
    )
    historical_relevant_state_id: Optional[uuid.UUID] = Field(default=None)
    historical_relevant_state_revision: Optional[int] = Field(default=None)
    anomaly_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="anomaly.id"
    )


class Anomaly(SQLModel, table=True):
    __table_args__ = (
        # UniqueConstraint(
        #     "start_time", "end_time", "symptom_id",
        #     name="anomaly_symptom_time"),
        {"extend_existing": True}
    )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    # revision: Optional[int] = Field(default=1)
    uri: Optional[str] = Field(default=None)
    state: Optional[State] = Field(default=State.unknown)
    description: Optional[str] = Field(default="")
    start_time: PastDatetime = Field(sa_type=DateTime)
    end_time: Optional[PastDatetime] = Field(sa_type=DateTime)
    confidence_score: float = Field(ge=0.0, le=1.0)
    pattern: Optional[AnomalyPattern] = Field(default=None)
    annotator_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="annotator.id"
    )
    annotator: Annotator = Relationship()
    symptom_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="symptom.id"
    )
    symptom: Symptom = Relationship()
    relevant_states: List["RelevantState"] = Relationship(
        back_populates="anomaly",
        link_model=RelevantStateAnomalyLink,
        sa_relationship_kwargs={
            "primaryjoin": "Anomaly.id==RelevantStateAnomalyLink.anomaly_id",
            "secondaryjoin":
                "RelevantState.id==RelevantStateAnomalyLink.relevant_state_id",
            "foreign_keys":
                "[RelevantStateAnomalyLink.anomaly_id, "
                "RelevantStateAnomalyLink.relevant_state_id]",
        }
    )
    historical_relevant_states: List["HistoricalRelevantState"] = Relationship(
        back_populates="anomaly",
        link_model=HistoricalRelevantStateAnomalyLink,
        sa_relationship_kwargs={
            "primaryjoin":
                "Anomaly.id==HistoricalRelevantStateAnomalyLink."
                "anomaly_id",
            "secondaryjoin":
                "and_(HistoricalRelevantState.id=="
                "HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_id, "
                "HistoricalRelevantState.revision=="
                "HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_revision)",
            "foreign_keys":
                "[HistoricalRelevantStateAnomalyLink.anomaly_id, "
                "HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_id, "
                "HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_revision]",
        }
    )

    def to_api_model(self) -> api.Anomaly:
        return api.Anomaly(
            id=self.id,
            # revision=self.revision,
            uri=self.uri,
            state=self.state,
            description=self.description,
            start_time=self.start_time,
            end_time=self.end_time,
            confidence_score=self.confidence_score,
            pattern=self.pattern,
            annotator=api.Annotator(
                name=self.annotator.name,
                version=self.annotator.version,
                annotator_type=self.annotator.annotator_type
            ) if self.annotator else None,
            symptom=api.Symptom(
                id=self.symptom.id,
                concern_score=self.symptom.concern_score,
                metric=self.symptom.metric,
                dimensions=self.symptom.dimensions
            ) if self.symptom else None
        )


class Publisher(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "version", name="publisher_version"),
        {"extend_existing": True}
    )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True)
    name: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)


class Service(SQLModel, table=True):
    __table_args__ = (
        {"extend_existing": True}
    )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True)
    type: Optional[str] = Field(default=None)
    data: Optional[dict] = Field(
        default=None, sa_column_kwargs={"nullable": True}, sa_type=JSONB
    )

    # Relationship to RelevantState
    relevant_states: List["RelevantState"] = Relationship(
        back_populates="service"
    )


class RelevantState(SQLModel, table=True):
    __table_args__ = (
        {"extend_existing": True}
    )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    revision: int = Field(default=1, ge=1)
    uri: Optional[str] = Field(default=None)
    description: Optional[str]
    start_time: PastDatetime = Field(sa_type=DateTime)
    end_time: Optional[PastDatetime] = Field(sa_type=DateTime)
    state: Optional[State] = Field(default=State.unknown)
    confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    concern_score: float = Field(ge=0.0, le=1.0, default=0.0)
    publisher_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="publisher.id"
    )
    publisher: Publisher = Relationship()
    service_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="service.id"
    )
    service: Optional[Service] = Relationship()
    anomaly: List[Anomaly] = Relationship(
        back_populates="relevant_states",
        link_model=RelevantStateAnomalyLink,
        sa_relationship_kwargs={
            "primaryjoin":
                "RelevantState.id==RelevantStateAnomalyLink."
                "relevant_state_id",
            "secondaryjoin":
                "Anomaly.id==RelevantStateAnomalyLink.anomaly_id",
            "foreign_keys":
                "[RelevantStateAnomalyLink.relevant_state_id, "
                "RelevantStateAnomalyLink.anomaly_id]",
        }
    )

    def to_api_model(self) -> api.RelevantState:
        return api.RelevantState(
            id=self.id,
            revision=self.revision,
            uri=self.uri,
            description=self.description,
            start_time=self.start_time,
            end_time=self.end_time,
            state=self.state,
            confidence_score=self.confidence_score,
            concern_score=self.concern_score,
            publisher=api.Publisher(
                name=self.publisher.name,
                version=self.publisher.version
            ) if self.publisher else None,
            service=api.Service(
                id=self.service.id,
                type=self.service.type
            ) if self.service else None,
            anomaly=[anomaly.to_api_model() for anomaly in self.anomaly]
        )


class HistoricalRelevantState(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint("id", "revision"),
        {"extend_existing": True}
    )

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4
    )
    revision: int = Field(default=1, ge=1)
    uri: Optional[str] = Field(default=None)
    description: Optional[str]
    start_time: PastDatetime = Field(sa_type=DateTime)
    end_time: Optional[PastDatetime] = Field(
        sa_type=DateTime, default=None)
    state: Optional[State] = Field(default=State.unknown)
    confidence_score: Optional[float] = Field(
        ge=0.0, le=1.0, default=0.0)
    concern_score: float = Field(
        ge=0.0, le=1.0, default=0.0)
    publisher_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="publisher.id"
    )
    publisher: Publisher = Relationship()
    service_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="service.id"
    )
    service: Optional[Service] = Relationship()
    anomaly: List[Anomaly] = Relationship(
        back_populates="historical_relevant_states",
        link_model=HistoricalRelevantStateAnomalyLink,
        sa_relationship_kwargs={
            "primaryjoin":
                "HistoricalRelevantState.id=="
                "HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_id "
                "and HistoricalRelevantState.revision=="
                "HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_revision",
            "secondaryjoin":
                "Anomaly.id==HistoricalRelevantStateAnomalyLink.anomaly_id",
            "foreign_keys":
                "[HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_id, "
                "HistoricalRelevantStateAnomalyLink."
                "historical_relevant_state_revision, "
                "HistoricalRelevantStateAnomalyLink.anomaly_id]",
        }
    )
