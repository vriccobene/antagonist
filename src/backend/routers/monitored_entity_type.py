import uuid
from typing import List
from sqlmodel import Session
from fastapi import status, Depends, APIRouter
from data_models.telemetry import api
from data_models.telemetry.api_request import (
    MonitoredEntityTypeRequest as Request,
    MonitoredEntityTypeResponse as Response
)
from views.monitored_entity_type_view import MonitoredEntityTypeView
from views.service_view import ServiceView
import dependencies
from fastapi import HTTPException


router = APIRouter(tags=["monitored-entity-type"])
router_existing_services = APIRouter(
    tags=["existing-monitored-entity-types-in-services"])


@router_existing_services.get(
    '',
    response_model=List[str],
    status_code=status.HTTP_200_OK)
@router_existing_services.get(
    '/',
    response_model=List[str],
    status_code=status.HTTP_200_OK)
async def get_existing_monitored_entity_types_from_services(
    db_session: Session = Depends(dependencies.get_session)
):
    unique_service_types = \
        ServiceView.get_unique_service_types(db_session)
    return unique_service_types


@router.get(
    '',
    response_model=Response | List[Response] | None,
    status_code=status.HTTP_200_OK)
@router.get(
    '/',
    response_model=Response | List[Response] | None,
    status_code=status.HTTP_200_OK)
@router.get(
    '/{name}',
    response_model=Response | List[Response] | None,
    status_code=status.HTTP_200_OK)
async def get(
    monitored_entity_request: Request = Depends(),
    db_session: Session = Depends(dependencies.get_session)
):

    res = MonitoredEntityTypeView.retrieve(
        monitored_entity_request, db_session)
    db_session.close()
    if isinstance(res, list):
        return [api.MonitoredEntityType.model_validate(
            item, from_attributes=True) for item in res]
    return res


@router.post('', response_model=dict, status_code=status.HTTP_200_OK)
@router.post('/', response_model=dict, status_code=status.HTTP_200_OK)
async def post(
        monitored_entity_type: Request,
        db_session: Session = Depends(dependencies.get_session)):
    res = MonitoredEntityTypeView.create(monitored_entity_type, db_session)
    db_session.close()

    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create monitored entity type."
        )

    if isinstance(res, dict) and "error" in res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res
        )

    return {
        "name": res.get('name'),
        "message": "Monitored entity type created successfully."
    }


@router.put('/{monitored_entity_type_id}', status_code=status.HTTP_200_OK)
async def update_monitored_entity_type(
    monitored_entity_type_id: uuid.UUID,
    monitored_entity_type: api.MonitoredEntityType,
    db_session: Session = Depends(dependencies.get_session)
):
    # Ensure the object has the correct ID set
    monitored_entity_type.id = monitored_entity_type_id
    res = MonitoredEntityTypeView.update(
        monitored_entity_type,
        db_session)
    db_session.close()
    return res
