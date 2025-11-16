import psycopg2
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from data_models.telemetry import db, api, api_request
from data_models.telemetry.api_request import (
    MonitoredEntityTypeResponse as Response)


class MonitoredEntityTypeView:

    @staticmethod
    def retrieve(
        monitored_entity_type_request:
            api_request.MonitoredEntityTypeRequest = None,
        db_session: Session = None
    ) -> api.MonitoredEntityType | List[api.MonitoredEntityType] | None:

        if monitored_entity_type_request:
            query = select(db.MonitoredEntityType)
            if monitored_entity_type_request.name:
                query = query.where(
                    db.MonitoredEntityType.name ==
                    monitored_entity_type_request.name)
            results = db_session.exec(query).all()

            # If a specific name was requested, return that single item or None
            if (monitored_entity_type_request.name) and len(results) == 1:
                r = results[0]
                return Response(
                    name=r.name,
                    description=r.description,
                    data_source=r.data_source.to_api_model()
                )
            # Otherwise, return a list
            output = []
            for r in results:
                output.append(
                    Response(
                        name=r.name,
                        description=r.description,
                        data_source=r.data_source.to_api_model()
                    )
                )
            return output
        return []

    @staticmethod
    def create(
        monitored_entity_type: api_request.MonitoredEntityTypeRequest,
        db_session: Session = None
    ) -> db.MonitoredEntityType | dict | None:
        """
        Create a new monitored entity type in the database.
        It is important to verify if the provided datasource ID
        exists before creating the entity type.
        If it does not exist, return None.
        Otherwise, create the entity type and return it (or an error dict).
        """

        if not monitored_entity_type or not db_session:
            return None

        # Check if data_source_id exists
        if hasattr(monitored_entity_type, "data_source_id") and \
                monitored_entity_type.data_source_id:
            datasource = db_session.get(
                db.DataSource, monitored_entity_type.data_source_id)
            if not datasource:
                return {
                    "error": "Referenced data_source_id does not exist.",
                    "message": "Provide a valid data_source_id or create "
                               "the DataSource first.",
                    "details": f"data_source_id="
                               f"{monitored_entity_type.data_source_id}"
                               " not found"
                }

        db_obj = db.MonitoredEntityType(
            name=monitored_entity_type.name,
            description=monitored_entity_type.description,
            data_source_id=getattr(
                monitored_entity_type, "data_source_id", None)
        )
        db_session.add(db_obj)

        try:
            db_session.commit()
        except IntegrityError as e:
            # SQLAlchemy wraps DB errors in IntegrityError; 
            # inspect the original DB error
            db_session.rollback()
            orig = getattr(e, "orig", None)
            if isinstance(orig, psycopg2.errors.UniqueViolation):
                # Duplicate unique constraint, likely name conflict
                return {
                    "error": "MonitoredEntityType already exists with "
                             "the same unique field.",
                    "message": "Rename the Monitored Entity Type or "
                               "remove the existing one.",
                    "details": str(orig) or str(e)
                }
            # Other integrity errors (foreign key, check constraint, etc.)
            return {
                "error": "A database integrity error occurred.",
                "message": "Check your input for invalid or conflicting "
                           "values.",
                "details": str(e)
            }
        except Exception as e:
            db_session.rollback()
            return {
                "error": "An unexpected database error occurred.",
                "message": "Please try again later or contact support with "
                           "the details.",
                "details": str(e)
            }
        db_session.refresh(db_obj)
        return db_obj.model_dump()

    @staticmethod
    def update(
        monitored_entity_type: api.MonitoredEntityType,
        db_session: Session = None
    ) -> db.MonitoredEntityType | None:

        if not monitored_entity_type or \
           not db_session or \
           not monitored_entity_type.id:
            return None

        db_obj = db_session.get(
            db.MonitoredEntityType, monitored_entity_type.id
        )
        if not db_obj:
            return None

        db_obj.name = monitored_entity_type.name
        db_obj.description = monitored_entity_type.description
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj
