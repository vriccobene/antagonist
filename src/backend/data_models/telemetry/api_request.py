import uuid
from typing import Optional
from pydantic import BaseModel, Field
from data_models.telemetry.api import DataSourceType, DataSource


class EndpointRequest(BaseModel):
    url: Optional[str] = Field(
        default=None,
        description="The URL of the endpoint")


class DataSourceRequest(BaseModel):
    id: Optional[uuid.UUID] = Field(
        default=None,
        description="The unique identifier of the data source")
    name: Optional[str] = Field(
        default=None,
        description="The name of the data source")
    description: Optional[str] = Field(
        default=None,
        description="Textual description for the data source")
    type: Optional[DataSourceType] = Field(
        default=None,
        description="The type of the data source")
    end_point: Optional[EndpointRequest] = Field(
        default=None,
        description="The main endpoint for the data source")


class MonitoredEntityTypeRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="The name of the monitored entity type")
    description: Optional[str] = Field(
        default=None,
        description="Textual description for the monitored entity type")
    data_source_id: Optional[uuid.UUID] = Field(
        default=None,
        description="The unique identifier of the data source this "
                    "entity type belongs to")


class MonitoredEntityTypeResponse(BaseModel):
    name: str
    description: Optional[str] = None
    data_source: Optional[DataSource] = None
