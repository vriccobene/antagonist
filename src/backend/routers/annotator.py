import uuid
from typing import List
from sqlmodel import Session
from fastapi import status, Depends, APIRouter
from data_models.label_store import api, api_request
from views.annotator_view import AnnotatorView
import dependencies


router = APIRouter(tags=["annotator"])


@router.get(
        '/', response_model=api.Annotator | List[api.Annotator],
        status_code=status.HTTP_200_OK)
async def get(
        annotator_request: api_request.AnnotatorRequest | None = None,
        db_session: Session = Depends(dependencies.get_session)
):
    res = AnnotatorView.retrieve(annotator_request, None, db_session)
    db_session.close()
    return res


@router.get(
        '/{annotator_name}',
        response_model=api.Annotator | List[api.Annotator] | None,
        status_code=status.HTTP_200_OK)
async def get_annotator(
        annotator_request: api_request.AnnotatorRequest | None = None,
        annotator_name: str | None = None,
        db_session: Session = Depends(dependencies.get_session)
):
    res = AnnotatorView.retrieve(annotator_request, annotator_name, db_session)
    db_session.close()
    return res


@router.post('/', response_model=uuid.UUID, status_code=status.HTTP_200_OK)
async def post(
        annotator: api.Annotator,
        db_session: Session = Depends(dependencies.get_session)
):
    res = AnnotatorView.create(annotator, db_session)
    db_session.close()
    return res


@router.put('/{annotator_id}', status_code=status.HTTP_200_OK)
async def put(
        annotator: api.Annotator,
        db_session: Session = Depends(dependencies.get_session)
):
    return AnnotatorView.update(annotator, db_session)
