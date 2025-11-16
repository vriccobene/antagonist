import uuid
from sqlmodel import Session
from typing import List, Optional
from fastapi import status, Depends, APIRouter, Query
from data_models.label_store import api
from data_models.label_store.common import State, AnomalyPattern
from data_models.label_store.api_request import (
    AnomalyRequest, parse_datetime_to_utc
)
from data_models.label_store.api import Annotator, Symptom
from views.anomaly_view import AnomalyView
import dependencies


router = APIRouter(tags=["anomaly"])


@router.get(
    '',
    response_model=List[api.Anomaly],
    status_code=status.HTTP_200_OK)
@router.get(
    '/',
    response_model=List[api.Anomaly],
    status_code=status.HTTP_200_OK)
@router.get(
    '/{id}',
    response_model=api.Anomaly | List[api.Anomaly] | None,
    status_code=status.HTTP_200_OK)
async def get(
        id: Optional[uuid.UUID] = None,
        ids: Optional[List[uuid.UUID]] = Query(default=None),
        state: Optional[State | List[State]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        symptom_id: Optional[uuid.UUID] = None,
        min_confidence_score: Optional[float] = Query(
            default=0.0, ge=0.0, le=1.0),
        max_confidence_score: Optional[float] = Query(
            default=1.0, ge=0.0, le=1.0),
        min_concern_score: Optional[float] = Query(
            default=0.0, ge=0.0, le=1.0),
        max_concern_score: Optional[float] = Query(
            default=1.0, ge=0.0, le=1.0),
        pattern: Optional[AnomalyPattern] = None,
        annotator: Optional[Annotator] = None,
        symptom: Optional[Symptom] = None,
        db_session: Session = Depends(dependencies.get_session)):

    # Manually parse datetime strings and create request object
    anomaly_request = AnomalyRequest(
        id=id,
        ids=ids,
        state=state,
        start_time=parse_datetime_to_utc(start_time),
        end_time=parse_datetime_to_utc(end_time),
        symptom_id=symptom_id,
        min_confidence_score=min_confidence_score,
        max_confidence_score=max_confidence_score,
        min_concern_score=min_concern_score,
        max_concern_score=max_concern_score,
        pattern=pattern,
        annotator=annotator,
        symptom=symptom
    )

    res = AnomalyView.retrieve(anomaly_request, db_session)
    db_session.close()
    return res


@router.post('/', response_model=uuid.UUID,
             status_code=status.HTTP_200_OK)
async def post(
        anomaly: api.Anomaly,
        db_session: Session = Depends(dependencies.get_session)):
    res = AnomalyView.create(anomaly, db_session)
    db_session.close()
    return res.id if hasattr(res, "id") else res


# @router.put('/{relevant_state_id}',
#             status_code=status.HTTP_200_OK)
# async def update_anomaly(
#         anomaly: api.Anomaly,
#         db_session: Session = Depends(dependencies.get_session)):
#     return AnomalyView.update(anomaly, db_session)
