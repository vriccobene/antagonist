import uuid
from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship
from data_models.telemetry import api


class DataSource(SQLModel, table=True):
    __table_args__ = (
        {"extend_existing": True}
    )
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: Optional[str] = None
    database_type: str
    database_version: str
    end_point_url: Optional[str] = None
    end_point_metadata: Optional[dict] = Field(
        default=None,
        sa_column_kwargs={"nullable": True},
        sa_type=JSONB
    )

    def to_api_model(self) -> api.DataSource:
        return api.DataSource(
            id=self.id,
            name=self.name,
            description=self.description,
            type=api.DataSourceType(
                database=self.database_type,
                version=self.database_version
            ),
            end_point=api.Endpoint(
                url=self.end_point_url,
                metadata=self.end_point_metadata
            )
        )


class MonitoredEntityType(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            'name', 'data_source_id',
            name='uix_data_source_entity'),
        {"extend_existing": True}
    )
    name: str = Field(primary_key=True, unique=True)
    description: Optional[str] = None
    data_source_id: uuid.UUID = Field(foreign_key="datasource.id")
    data_source: Optional["DataSource"] = Relationship(
        sa_relationship_kwargs={"uselist": False, "lazy": "joined"}
    )
