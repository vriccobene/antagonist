import uuid
import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, PastDatetime

from .common import AnnotatorType, AnomalyPattern, State


class Symptom(BaseModel):
    concern_score: float = Field(ge=0.0, le=1.0)


class Annotator(BaseModel):
    name: str
    version: Optional[int] = Field(default=0)
    annotator_type: AnnotatorType


class Anomaly(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    # TODO DRAFT This field (revision) is in the IETF draft,
    # but I think should be removed
    # revision: Optional[int] = Field(default=1)
    uri: Optional[str] = Field(default=None)
    state: State = Field(default=State.unknown)
    description: Optional[str] = Field(default="")
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = Field(default=None)
    confidence_score: float = Field(ge=0.0, le=1.0)
    pattern: Optional[AnomalyPattern] = Field(default=None)
    annotator: Annotator
    symptom: Optional[Symptom] = Field(default={})


class Publisher(BaseModel):
    name: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)


class Service(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)


class RelevantState(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    revision: int = Field(default=1, ge=1)
    uri: Optional[str] = Field(default=None)
    description: Optional[str]
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = Field(default=None)
    state: State  # TODO DRAFT This is currently not in the IETF model
    confidence_score: Optional[float] = Field(ge=0.0, le=1.0)
    concern_score: float = Field(ge=0.0, le=1.0)
    publisher: Publisher
    service: Optional[Service]
    anomaly: Optional[List[Anomaly]] = Field(default_factory=list)
