import uuid
import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, AwareDatetime, field_validator
from .api import Publisher
from .common import AnnotatorType, AnomalyPattern, State
from .api import Annotator, Service, Symptom


def parse_datetime_to_utc(v):
    """
    Parse datetime value and ensure it's in UTC timezone.
    Handles date-only strings (YYYY-MM-DD), full ISO datetime strings,
    and datetime objects.
    """
    if v is None:
        return v
    
    if isinstance(v, str):
        # Handle date-only format (YYYY-MM-DD)
        if len(v) == 10 and v.count('-') == 2:
            # Parse as date and set to start of day UTC
            v = v + 'T00:00:00Z'
        # Parse ISO format string
        dt = datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
    elif isinstance(v, datetime.datetime):
        dt = v
    else:
        return v

    # Ensure timezone awareness
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    elif dt.tzinfo != datetime.timezone.utc:
        dt = dt.astimezone(datetime.timezone.utc)
    
    return dt


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
    ids: Optional[List[uuid.UUID]] = Field(default=None)
    state: Optional[State | List[State]] = Field(default=None)
    start_time: Optional[AwareDatetime] = Field(default=None)
    end_time: Optional[AwareDatetime] = Field(default=None)
    symptom_id: Optional[uuid.UUID] = Field(default=None)
    min_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    pattern: Optional[AnomalyPattern] = Field(default=None)
    annotator: Optional[Annotator] = Field(default=None)
    symptom: Optional[Symptom] = Field(default=None)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, v):
        """Ensure datetime is in UTC timezone"""
        return parse_datetime_to_utc(v)


class AnomalyUpdateRequest(BaseModel):
    """
    This class is used to represent a request for anomalies.
    """
    id: Optional[uuid.UUID] = Field(default=None)
    # revision: Optional[int] = Field(default=1)
    state: Optional[State | List[State]] = Field(default=None)
    start_time: Optional[AwareDatetime] = Field(default=None)
    end_time: Optional[AwareDatetime] = Field(default=None)
    symptom_id: Optional[uuid.UUID] = Field(default=None)
    min_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    pattern: Optional[AnomalyPattern] = Field(default=None)
    annotator: Optional[Annotator] = Field(default=None)
    symptom: Optional[Symptom] = Field(default=None)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, v):
        """Ensure datetime is in UTC timezone"""
        return parse_datetime_to_utc(v)


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
    start_time: Optional[AwareDatetime] = Field(default=None)
    end_time: Optional[AwareDatetime] = Field(default=None)
    state: Optional[State] = Field(default=None)
    max_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_concern_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    max_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    min_confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    service_id: Optional[uuid.UUID] = Field(default=None)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, v):
        """Ensure datetime is in UTC timezone"""
        return parse_datetime_to_utc(v)


class RelevantStateUpdateRequest(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    revision: int = Field(default=None, ge=1)
    uri: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    start_time: AwareDatetime = Field(default=None)
    end_time: Optional[AwareDatetime] = Field(default=None)
    # TODO DRAFT This is currently not in the IETF model
    state: Optional[State] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    concern_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    publisher: Optional[Publisher] = Field(default=None)
    service: Optional[Service] = Field(default=None)
    anomaly: Optional[List[AnomalyUpdateRequest]] = Field(default=None)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, v):
        """Ensure datetime is in UTC timezone"""
        return parse_datetime_to_utc(v)
