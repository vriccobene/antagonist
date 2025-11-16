import uuid
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel


class DatabaseType(StrEnum):
    INFLUXDB = "influxdb"
    # PROMETHEUS = "prometheus"
    # GRAPHITE = "graphite"
    # ELASTICSEARCH = "elasticsearch"
    # CUSTOM = "custom"


class DataSourceType(BaseModel):
    database: DatabaseType
    version: str


class Endpoint(BaseModel):
    url: str
    metadata: Optional[dict] = dict()


class DataSource(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    type: DataSourceType
    end_point: Endpoint


class Unit(BaseModel):
    name: str
    symbol: str
    description: Optional[str] = None


class Metric(BaseModel):
    name: str
    description: Optional[str] = None
    unit: Optional[Unit] = None


class Field(BaseModel):
    name: str
    description: Optional[str] = None


class MonitoredEntityType(BaseModel):
    name: str
    description: Optional[str] = None
    data_source: Optional[DataSource] = None
