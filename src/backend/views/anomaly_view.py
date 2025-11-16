from datetime import timedelta
import uuid
from typing import List
from sqlmodel import Session, or_, select
from sqlalchemy.orm import joinedload
from data_models.label_store import db, api, api_request
from data_models.label_store.db import (
    Anomaly, Annotator, Symptom
)
from views import annotator_view, symptom_view, service_view, publisher_view


class AnomalyView:

    def retrieve(
            anomaly_request: api_request.AnomalyRequest = None,
            db_session: Session = None) -> api.Anomaly | List[api.Anomaly]:
        """
        Retrieve an anomaly by its ID or all anomalies if no ID is provided.
        """

        statement = select(db.Anomaly)
        statement = statement.options(
            joinedload(db.Anomaly.symptom),
            joinedload(db.Anomaly.annotator),
        )
        if anomaly_request.id:
            statement = statement.where(db.Anomaly.id == anomaly_request.id)
            return db_session.exec(statement).unique().first()
        else:
            if anomaly_request.start_time:
                statement = statement.where(
                    db.Anomaly.start_time >= anomaly_request.start_time)
            if anomaly_request.end_time:
                statement = statement.where(
                    or_(
                        db.Anomaly.end_time <=
                        anomaly_request.end_time + timedelta(days=1),
                        db.Anomaly.end_time == None
                    )
                )
            if anomaly_request.state:
                statement = statement.where(
                    db.Anomaly.state.in_(
                        anomaly_request.state
                        if isinstance(anomaly_request.state, List)
                        else [anomaly_request.state]
                    )
                )
            if anomaly_request.max_confidence_score is not None:
                statement = statement.where(
                    db.Anomaly.confidence_score <=
                    anomaly_request.max_confidence_score)
            if anomaly_request.min_confidence_score is not None:
                statement = statement.where(
                    db.Anomaly.confidence_score >=
                    anomaly_request.min_confidence_score)
            if anomaly_request.max_concern_score is not None and \
                    anomaly_request.symptom and \
                    anomaly_request.symptom.concern_score:
                statement = statement.where(
                    db.Anomaly.symptom.concern_score <=
                    anomaly_request.max_concern_score)
            if anomaly_request.min_concern_score is not None and \
                    anomaly_request.symptom and \
                    anomaly_request.symptom.concern_score:
                statement = statement.where(
                    db.Anomaly.symptom.concern_score >=
                    anomaly_request.min_concern_score)
        return db_session.exec(statement).unique().all()

    @staticmethod
    def create(anomaly: api.Anomaly, db_session: Session) -> db.Anomaly:
        """
        Create a new service in the database
        """

        # existing_anomaly = db_session.exec(select(db.Anomaly).where(and_(
        #     db.Anomaly.start_time == anomaly.start_time, 
        #     db.Anomaly.end_time == anomaly.end_time,
        #     db.Anomaly.symptom_id == anomaly.symptom.id,
        # ))).first()
        # if not existing_anomaly:
        # Convert nested objects if present
        res = db.Anomaly.model_validate(anomaly.model_dump())

        if anomaly.symptom:
            symptom = symptom_view.SymptomView.create(
                anomaly.symptom, db_session)
            res.symptom_id = symptom.id
        if anomaly.annotator:
            annotator = annotator_view.AnnotatorView.create(
                anomaly.annotator, db_session)
            res.annotator_id = annotator.id
        if hasattr(anomaly, "publisher") and anomaly.publisher:
            publisher = publisher_view.PublisherView.create(
                anomaly.publisher, db_session, commit=False)
            res.publisher_id = publisher.id
        if hasattr(anomaly, "service") and anomaly.service:
            service = service_view.ServiceView.create(
                anomaly.service, db_session)
            res.service_id = service.id

        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        return res

    @staticmethod
    def update(anomaly: api.Anomaly, db_session: Session) -> db.Anomaly:
        """
        Update an existing anomaly in the database.
        """
        existing_anomaly = db_session.exec(
            select(db.Anomaly).where(db.Anomaly.id == anomaly.id)
        ).first()
        if not existing_anomaly:
            raise ValueError(f"Anomaly with ID {anomaly.id} does not exist.")
        existing_anomaly_data = db.Anomaly.model_validate(anomaly)
        existing_anomaly.start_time = existing_anomaly_data.start_time
        existing_anomaly.end_time = existing_anomaly_data.end_time
        existing_anomaly.symptom_id = existing_anomaly_data.symptom_id
        existing_anomaly.publisher_id = existing_anomaly_data.publisher_id
        existing_anomaly.service_id = existing_anomaly_data.service_id
        existing_anomaly.annotator_id = existing_anomaly_data.annotator_id
        db_session.add(existing_anomaly)
        db_session.commit()
        db_session.refresh(existing_anomaly)
        return existing_anomaly
