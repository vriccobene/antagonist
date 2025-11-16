import uuid
from typing import List
from sqlmodel import Session, select
from data_models.label_store import db, api


class ServiceView:

    @staticmethod
    def retrieve(
        service_id: uuid.UUID = None,
        db_session: Session = None
    ) -> api.Service | List[api.Service]:
        """
        Retrieve all service IDs
        """
        if service_id:
            statement = select(db.Service).where(db.Service.id == service_id)
            db_service = db_session.exec(statement).first()
            if db_service:
                return ServiceView._to_api_model(db_service)
            return None
        statement = select(db.Service)
        db_services = db_session.exec(statement).all()
        return [ServiceView._to_api_model(service) for service in db_services]
    
    @staticmethod
    def _to_api_model(db_service: db.Service) -> api.Service:
        """
        Convert db.Service to api.Service, flattening the data field
        """
        service_dict = {
            "id": db_service.id,
            "type": db_service.type,
        }
        # Flatten the data field into the main object
        if db_service.data:
            service_dict.update(db_service.data)
        return api.Service(**service_dict)

    @staticmethod
    def create(service: api.Service, db_session: Session):
        """
        Create a new service in the database.
        """
        res = db.Service.model_validate(service)
        known_fields = set(api.Service.model_fields.keys())
        extra_fields = {k: v for k, v in dict(service).items()
                        if k not in known_fields}
        if extra_fields:
            res.data = extra_fields
        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        return res.id

    @staticmethod
    def update(service: api.Service, db_session: Session):
        pass

    @staticmethod
    def get_unique_service_types(
        db_session: Session
    ) -> List[str]:
        """
        Retrieve all unique service types from the Service table.
        """
        statement = select(db.Service.type).distinct()
        results = db_session.exec(statement).all()
        return results

    @staticmethod
    def get_relevant_states(
        service_id: uuid.UUID,
        db_session: Session
    ) -> List[api.RelevantState]:
        """
        Retrieve relevant states for a given service ID.
        """
        statement = select(db.RelevantState).where(
            db.RelevantState.service_id == service_id
        )
        relevant_states = db_session.exec(statement).all()
        return [rs.to_api_model() for rs in relevant_states]
