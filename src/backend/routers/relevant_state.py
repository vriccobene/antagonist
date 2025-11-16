import uuid
from typing import List, Optional
from sqlmodel import Session
from fastapi import status, Depends, APIRouter, Query
from data_models.label_store import api
from data_models.label_store.common import State
from data_models.label_store.api_request import (
    RelevantStateRequest, parse_datetime_to_utc
)
from views.relevant_state_view import RelevantStateView
import dependencies


router = APIRouter(tags=["relevant_state"])


@router.get(
        '', response_model=List[api.RelevantState],
        status_code=status.HTTP_200_OK)
@router.get(
        '/', response_model=List[api.RelevantState],
        status_code=status.HTTP_200_OK)
@router.get(
        '/{id}', response_model=api.RelevantState | List[api.RelevantState],
        status_code=status.HTTP_200_OK)
async def get(
        id: Optional[uuid.UUID] = None,
        revision: Optional[int] = Query(default=None, ge=1),
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        state: Optional[State] = None,
        max_concern_score: Optional[float] = Query(
            default=1.0, ge=0.0, le=1.0),
        min_concern_score: Optional[float] = Query(
            default=0.0, ge=0.0, le=1.0),
        max_confidence_score: Optional[float] = Query(
            default=1.0, ge=0.0, le=1.0),
        min_confidence_score: Optional[float] = Query(
            default=0.0, ge=0.0, le=1.0),
        service_id: Optional[uuid.UUID] = None,
        db_session: Session = Depends(dependencies.get_session)):

    # Manually parse datetime strings and create request object
    relevant_state_request = RelevantStateRequest(
        id=id,
        revision=revision,
        start_time=parse_datetime_to_utc(start_time),
        end_time=parse_datetime_to_utc(end_time),
        state=state,
        max_concern_score=max_concern_score,
        min_concern_score=min_concern_score,
        max_confidence_score=max_confidence_score,
        min_confidence_score=min_confidence_score,
        service_id=service_id
    )

    res = RelevantStateView.retrieve(
        relevant_state_request, db_session)
    db_session.close()
    return res


@router.post('', response_model=uuid.UUID, status_code=status.HTTP_200_OK)
@router.post('/', response_model=uuid.UUID, status_code=status.HTTP_200_OK)
async def post(
        relevant_state: api.RelevantState,
        db_session: Session = Depends(dependencies.get_session)):

    res = RelevantStateView.create(relevant_state, db_session)
    db_session.close()
    return res


@router.put(
        '/{relevant_state_id}',
        status_code=status.HTTP_200_OK
)
async def put(
        relevant_state: api.RelevantState,
        db_session: Session = Depends(dependencies.get_session)):

    return RelevantStateView.update(
        relevant_state, db_session)
