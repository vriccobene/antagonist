import uuid
from typing import List
from sqlmodel import Session
from fastapi import status, Depends, APIRouter
from data_models.telemetry import api, api_request
from views.data_source_view import DataSourceView
import dependencies
import logging
from utils import logger
from fastapi.encoders import jsonable_encoder

# Configure logging
log = logging.getLogger(__name__)

router = APIRouter(tags=["data_source"])


@router.get(
    '',
    response_model=List[api.DataSource],
    status_code=status.HTTP_200_OK)
@router.get(
    '/',
    response_model=List[api.DataSource],
    status_code=status.HTTP_200_OK)
@router.get(
    '/{id}',
    response_model=api.DataSource | List[api.DataSource] | None,
    status_code=status.HTTP_200_OK)
async def get(
        data_source_request: api_request.DataSourceRequest = Depends(),
        db_session: Session = Depends(dependencies.get_session)):

    res = DataSourceView.retrieve(data_source_request, db_session)
    db_session.close()
    if isinstance(res, list):
        res = jsonable_encoder([
            api.DataSource.model_validate(
                item, from_attributes=True).model_dump()
            for item in res
        ])
        return res
    log.info("DataSourceView.retrieve result: %r", res)
    return res.model_dump() if res else None


@router.post('', response_model=uuid.UUID,
             status_code=status.HTTP_200_OK)
@router.post('/', response_model=uuid.UUID,
             status_code=status.HTTP_200_OK)
async def post(
        data_source: api.DataSource,
        db_session: Session = Depends(dependencies.get_session)):
    res = DataSourceView.create(data_source, db_session)
    db_session.close()
    return res.id if hasattr(res, "id") else res


@router.put('/{data_source_id}',
            status_code=status.HTTP_200_OK)
async def update_data_source(
        data_source_id: uuid.UUID,
        data_source: api.DataSource,
        db_session: Session = Depends(dependencies.get_session)):

    data_source.id = data_source_id
    return DataSourceView.update(data_source, db_session)
