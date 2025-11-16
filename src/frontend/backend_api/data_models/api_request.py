import uuid
import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, PastDatetime

from .api import Publisher, Anomaly
from .common import AnnotatorType, AnomalyPattern, State
from .api import Annotator, Service, Symptom


class AnnotatorRequest(BaseModel):
    """
    This class is used to represent a request for annotators.
    """
    id: Optional[uuid.UUID] = Field(default=None)
    name: str
    version: Optional[int] = Field(default=0)
    annotator_type: AnnotatorType


class AnomalyRequest(BaseModel):
    """
    This class is used to represent a request for anomalies.
    """
    id: Optional[uuid.UUID] = Field(default=None)
    # revision: Optional[int] = Field(default=1)
    state: Optional[State | List[State]] = Field(default=None)
    start_time: Optional[datetime.datetime] = Field(default=None)
    end_time: Optional[datetime.datetime] = Field(default=None)
    symptom_id: Optional[uuid.UUID] = Field(default=None)
    min_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    pattern: Optional[AnomalyPattern] = Field(default=None)
    annotator: Optional[Annotator] = Field(default=None)
    symptom: Optional[Symptom] = Field(default=None)


class AnomalyUpdateRequest(BaseModel):
    """
    This class is used to represent a request for anomalies.
    """
    id: Optional[uuid.UUID] = Field(default=None)
    # revision: Optional[int] = Field(default=1)
    state: Optional[State | List[State]] = Field(default=None)
    start_time: Optional[datetime.datetime] = Field(default=None)
    end_time: Optional[datetime.datetime] = Field(default=None)
    symptom_id: Optional[uuid.UUID] = Field(default=None)
    min_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    pattern: Optional[AnomalyPattern] = Field(default=None)
    annotator: Optional[Annotator] = Field(default=None)
    symptom: Optional[Symptom] = Field(default=None)


class ServiceRequest(BaseModel):
    """
    This class is used to represent a request for services.
    """
    id: Optional[uuid.uuid4] = Field(default=None)


class RelevantStateRequest(BaseModel):
    """
    This class is used to represent a request for a relevant state.
    """
    id: Optional[uuid.UUID] = Field(default=None)
    revision: Optional[int] = Field(default=None, ge=1)
    start_time: Optional[datetime.datetime] = Field(default=None)
    end_time: Optional[datetime.datetime] = Field(default=None)
    state: Optional[State] = Field(default=None)
    max_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    service_id: Optional[uuid.UUID] = Field(default=None)


class RelevantStateUpdateRequest(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    revision: int = Field(default=None, ge=1)
    uri: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    start_time: datetime.datetime = Field(default=None)
    end_time: Optional[datetime.datetime] = Field(default=None)
    # TODO DRAFT This is currently not in the IETF model
    state: Optional[State] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    concern_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    publisher: Optional[Publisher] = Field(default=None)
    service: Optional[Service] = Field(default=None)
    anomaly: Optional[List[AnomalyUpdateRequest]] = Field(default=None)
