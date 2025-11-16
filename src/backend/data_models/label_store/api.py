import uuid
import datetime
from typing import Optional, List, Dict
from pydantic import (
    BaseModel, ConfigDict, Field, AwareDatetime, field_validator
)

from .common import AnnotatorType, AnomalyPattern, State


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


class Symptom(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    concern_score: float = Field(ge=0.0, le=1.0, default=1.0)
    model_config = ConfigDict(extra='allow')

    # TODO These two fields are not in the IETF draft
    metric: Optional[str] = Field(default="")
    dimensions: Optional[Dict[str, str | int | float]] = Field(default={})


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
    start_time: AwareDatetime
    end_time: Optional[AwareDatetime] = Field(default=None)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    pattern: Optional[AnomalyPattern] = Field(default=None)
    annotator: Annotator
    symptom: Optional[Symptom] = Field(default={})
    # This is not required in the IETF draft, but useful for frontend
    telemetry_data: Optional[Dict] = Field(default={})

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, v):
        """Ensure datetime is in UTC timezone"""
        return parse_datetime_to_utc(v)


class Publisher(BaseModel):
    name: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)


class Service(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    type: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra='allow')


class RelevantState(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None)
    revision: int = Field(default=1, ge=1)
    uri: Optional[str] = Field(default=None)
    description: Optional[str]
    start_time: AwareDatetime
    end_time: Optional[AwareDatetime] = Field(default=None)
    state: State  # TODO DRAFT This is currently not in the IETF model
    confidence_score: Optional[float] = Field(ge=0.0, le=1.0, default=0.0)
    concern_score: float = Field(ge=0.0, le=1.0, default=1.0)
    publisher: Publisher
    service: Optional[Service]
    anomaly: Optional[List[Anomaly]] = Field(default_factory=list)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, v):
        """Ensure datetime is in UTC timezone"""
        return parse_datetime_to_utc(v)
