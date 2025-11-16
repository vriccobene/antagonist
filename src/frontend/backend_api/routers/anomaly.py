import uuid
from typing import List
from sqlmodel import Session
from fastapi import status, Depends, APIRouter
from data_models import api, api_request
from views.anomaly_view import AnomalyView
import dependencies


router = APIRouter(tags=["anomaly"])


@router.get(
        '/',
        response_model=List[api.Anomaly],
        status_code=status.HTTP_200_OK)
@router.get(
    '/{anomaly_id}',
    response_model=api.Anomaly | List[api.Anomaly] | None,
    status_code=status.HTTP_200_OK)
async def get(
        anomaly_request: api_request.AnomalyRequest,
        anomaly_id: uuid.UUID | None = None,
        db_session: Session = Depends(dependencies.get_session)):

    res = AnomalyView.retrieve(anomaly_request, anomaly_id, db_session)
    db_session.close()
    return res


@router.post('/', response_model=uuid.UUID,
             status_code=status.HTTP_200_OK)
async def post(
        anomaly: api.Anomaly, 
        db_session: Session = Depends(dependencies.get_session)):
    res = AnomalyView.create(anomaly, db_session)
    db_session.close()
    return res


@router.put('/{relevant_state_id}', 
            status_code=status.HTTP_200_OK)
async def update_relevant_state(
        anomaly: api.Anomaly,
        db_session: Session = Depends(dependencies.get_session)):
    return AnomalyView.update(anomaly, db_session)
