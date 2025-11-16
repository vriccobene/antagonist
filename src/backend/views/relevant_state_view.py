import uuid
from typing import List
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from datetime import timedelta
from data_models.label_store.db import (
    RelevantState, Anomaly, State, HistoricalRelevantState
)
from data_models.label_store import api, db, api_request
from . import service_view, publisher_view, annotator_view, symptom_view


class RelevantStateView:

    @staticmethod
    def retrieve(
            relevant_state_request: api_request.RelevantStateRequest,
            db_session: Session
            ) -> api.RelevantState | List[api.RelevantState]:

        statement = select(db.RelevantState)
        statement = statement.options(
            joinedload(db.RelevantState.anomaly),
            joinedload(db.RelevantState.anomaly).joinedload(
                db.Anomaly.symptom),
            joinedload(db.RelevantState.anomaly).joinedload(
                db.Anomaly.annotator),
            joinedload(db.RelevantState.publisher),
            joinedload(db.RelevantState.service),
        )
        if relevant_state_request.id:
            statement = statement.where(
                db.RelevantState.id == relevant_state_request.id)
            return db_session.exec(statement).unique().first()
        else:
            if relevant_state_request.start_time:
                statement = statement.where(
                    db.RelevantState.start_time >=
                    relevant_state_request.start_time)
            if relevant_state_request.end_time:
                statement = statement.where(
                    or_(
                        db.RelevantState.end_time <=
                        relevant_state_request.end_time + timedelta(days=1),
                        db.RelevantState.end_time == None
                    )
                )
            if relevant_state_request.state:
                if relevant_state_request.state == State.anomaly:
                    statement = statement.where(
                        or_(
                            db.RelevantState.state == State.unknown,
                            db.RelevantState.state == State.forecasted,
                            db.RelevantState.state == State.potential,
                            db.RelevantState.state == State.discarded
                        )
                    )
                elif relevant_state_request.state == State.incident:
                    print("Filtering for incidents")
                    statement = statement.where(
                        or_(
                            db.RelevantState.state == State.confirmed,
                            db.RelevantState.state == State.analyzed,
                            db.RelevantState.state == State.adjusted
                        )
                    )
                    print(f"Statement: {statement}")
                else:
                    statement = statement.where(
                        db.RelevantState.state ==
                        relevant_state_request.state)
            if relevant_state_request.max_confidence_score is not None:
                statement = statement.where(
                    db.RelevantState.confidence_score <=
                    relevant_state_request.max_confidence_score)
            if relevant_state_request.min_confidence_score is not None:
                statement = statement.where(
                    db.RelevantState.confidence_score >=
                    relevant_state_request.min_confidence_score)
            if relevant_state_request.max_concern_score is not None:
                statement = statement.where(
                    db.RelevantState.concern_score <=
                    relevant_state_request.max_concern_score)
            if relevant_state_request.min_concern_score is not None:
                statement = statement.where(
                    db.RelevantState.concern_score >=
                    relevant_state_request.min_concern_score)
            if relevant_state_request.service_id:
                statement = statement.where(
                    db.RelevantState.service_id ==
                    relevant_state_request.service_id)
        return db_session.exec(statement).unique().all()

    @staticmethod
    def create(
            relevant_state: api.RelevantState,
            db_session: Session
            ) -> uuid.UUID:

        publisher = publisher_view.PublisherView.create(
            relevant_state.publisher, db_session, commit=False)
        # Check if service already exists (by unique name)
        existing_service = db_session.exec(
            select(db.Service).where(
                db.Service.id == relevant_state.service.id)
        ).first()
        if existing_service:
            service = existing_service.id
        else:
            service = service_view.ServiceView.create(
                relevant_state.service, db_session)
        anomalies = list()
        for anomaly_dict in relevant_state.anomaly or list():
            anomaly = Anomaly.model_validate(anomaly_dict)
            annotator = annotator_view.AnnotatorView.create(
                anomaly_dict.annotator, db_session)
            anomaly.annotator = annotator
            symptom = symptom_view.SymptomView.create(
                anomaly_dict.symptom, db_session)
            anomaly.symptom = symptom
            ano = Anomaly.model_validate(anomaly)
            ano.symptom_id = symptom.id
            ano.annotator_id = annotator.id
            anomalies.append(ano)

        db_relevant_state = RelevantState(
            uri=relevant_state.uri,
            description=relevant_state.description,
            state=relevant_state.state,
            start_time=relevant_state.start_time,
            end_time=relevant_state.end_time,
            confidence_score=relevant_state.confidence_score,
            concern_score=relevant_state.concern_score,
            publisher_id=publisher.id,
            service_id=service,
            anomaly=anomalies
        )
        # db_relevant_state = RelevantState.model_validate(relevant_state)
        db_session.add(db_relevant_state)
        db_session.commit()
        db_session.refresh(db_relevant_state)
        return db_relevant_state.id

    @staticmethod
    def update(relevant_state: api.RelevantState, db_session: Session):
        # Fetch the existing relevant state by id and revision
        db_relevant_state = db_session.exec(
            select(db.RelevantState)
            .where(db.RelevantState.id == relevant_state.id)
            .where(db.RelevantState.revision == relevant_state.revision - 1)
            .options(joinedload(db.RelevantState.anomaly))
        ).first()
        if not db_relevant_state:
            return None

        try:
            # Create a new entry in HistoricalRelevantState
            historical = HistoricalRelevantState.model_validate(
                db_relevant_state)
            db_session.add(historical)
            db_session.flush()  # To get historical.id

            # Update the db_relevant_state with the new values
            db_relevant_state.uri = relevant_state.uri or db_relevant_state.uri
            db_relevant_state.description = relevant_state.description or db_relevant_state.description
            db_relevant_state.start_time = relevant_state.start_time or db_relevant_state.start_time
            db_relevant_state.end_time = relevant_state.end_time or db_relevant_state.end_time
            db_relevant_state.state = relevant_state.state or db_relevant_state.state
            db_relevant_state.confidence_score = relevant_state.confidence_score or db_relevant_state.confidence_score
            db_relevant_state.concern_score = relevant_state.concern_score or db_relevant_state.concern_score
            db_relevant_state.revision += 1
            db_session.add(db_relevant_state)

            if relevant_state.anomaly is not None:
                db_relevant_state.anomaly.clear()
                for anomaly_obj in relevant_state.anomaly:
                    db_anomaly = db_session.get(Anomaly, getattr(anomaly_obj, "id", None))
                    if not db_anomaly:
                        anomaly = Anomaly.model_validate(anomaly_obj)
                        annotator = annotator_view.AnnotatorView.create(
                            anomaly_obj.annotator, db_session)
                        anomaly.annotator = annotator
                        anomaly_obj.symptom.id = None
                        symptom = symptom_view.SymptomView.create(
                            anomaly_obj.symptom, db_session)
                        anomaly.symptom = symptom
                        anomaly = Anomaly.model_validate(anomaly)
                        anomaly.symptom_id = symptom.id
                        anomaly.annotator_id = annotator.id
                        db_relevant_state.anomaly.append(anomaly)
                    else:
                        db_relevant_state.anomaly.append(db_anomaly)

            db_session.commit()
            db_session.refresh(db_relevant_state)
            return db_relevant_state
        except Exception as e:
            db_session.rollback()
            raise e

    # @staticmethod
    # def _get_anomaly(anomaly_obj):
