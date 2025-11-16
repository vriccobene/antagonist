import uuid
from typing import List
from sqlmodel import Session
from fastapi import status, Depends, APIRouter
from data_models import api, api_request
from views.relevant_state_view import RelevantStateView
import dependencies


router = APIRouter(tags=["relevant_state"])


@router.get('/', response_model=List[api.RelevantState], 
         status_code=status.HTTP_200_OK)
async def get(
        relevant_state_request: api_request.RelevantStateRequest, 
        db_session: Session = Depends(dependencies.get_session)):
    
    res = RelevantStateView.retrieve(
        relevant_state_request, db_session)
    db_session.close()
    return res


@router.post('/', response_model=uuid.UUID,status_code=status.HTTP_200_OK)
async def post(
        relevant_state: api.RelevantState,
        db_session: Session = Depends(dependencies.get_session)):

    res = RelevantStateView.create(relevant_state, db_session)
    db_session.close()
    return res


@router.put('/{relevant_state_id}', 
         status_code=status.HTTP_200_OK
)
async def put(
        relevant_state: api.RelevantState,
        db_session: Session = Depends(dependencies.get_session)):
    
    return RelevantStateView.update(
        relevant_state, db_session)
