import uuid
from typing import List
from sqlmodel import Session
from fastapi import status, Depends, APIRouter
from data_models.label_store import api

import dependencies
from views.service_view import ServiceView


router = APIRouter(tags=["service"])

# TODO The management of services needs to be integrated with the feature store


@router.get(
        '/', response_model=List[api.Service],
        status_code=status.HTTP_200_OK)
async def get(
        # service_request: api_request.ServiceRequest,
        db_session: Session = Depends(dependencies.get_session)):

    res = ServiceView.retrieve(db_session=db_session)
    db_session.close()
    return res


@router.get(
        '/{service_id}', response_model=List[api.Service],
        status_code=status.HTTP_200_OK)
async def get_id(
        service_id: uuid.UUID,
        # service_request: api_request.ServiceRequest,
        db_session: Session = Depends(dependencies.get_session)):

    res = ServiceView.retrieve(service_id, db_session)
    db_session.close()
    return res


@router.get(
        '/{service_id}/relevant_states',
        response_model=List[api.RelevantState],
        status_code=status.HTTP_200_OK)
async def get_relevant_states(
        service_id: uuid.UUID,
        # service_request: api_request.ServiceRequest,
        db_session: Session = Depends(dependencies.get_session)):   
    """
    Retrieve relevant states for a given service ID
    """
    return ServiceView.get_relevant_states(service_id, db_session)


# @router.get('/', response_model=List[api.Service],
#             status_code=status.HTTP_200_OK)
# async def get(
#         service_request: api_request.ServiceRequest,
#         db_session: Session = Depends(dependencies.get_session)
#     ):
#     res = ServiceView.retrieve(service_request, db_session)
#     db_session.close()
#     return res


# @router.get('/{service_id}', response_model=List[api.Service],
#          status_code=status.HTTP_200_OK)
# async def get(
#         service_id: uuid.UUID,
#         # service_request: api_request.ServiceRequest,
#         db_session: Session = Depends(dependencies.get_session)):

#     res = ServiceView.retrieve(service_id, db_session)
#     db_session.close()
#     return res


@router.post(
        '/', response_model=uuid.UUID,
        status_code=status.HTTP_200_OK)
async def post(
        service: api.Service,
        db_session: Session = Depends(dependencies.get_session)):

    res = ServiceView.create(service, db_session)
    db_session.close()
    return res


@router.put(
        '/{service_id}',
        status_code=status.HTTP_200_OK
)
async def update(
        service: api.Service,
        db_session: Session = Depends(dependencies.get_session)):

    return ServiceView.update(service, db_session)
