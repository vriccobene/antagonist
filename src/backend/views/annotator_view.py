import uuid
from typing import List
from sqlmodel import Session, select, and_
from data_models.label_store import db, api, api_request


class AnnotatorView:

    @staticmethod
    def retrieve(
        annotator_request: api_request.AnnotatorRequest = None,
        annotator_name: str | None = None,
        db_session: Session = None
    ) -> db.Annotator | List[db.Annotator] | None:

        if not annotator_name:
            # Retrun all annotators
            statement = select(db.Annotator)
            annotators = db_session.exec(statement).all()
            return annotators
        # Select based on Annotator ID
        statement = select(db.Annotator).where(
            db.Annotator.name == annotator_name)
        annotator = db_session.exec(statement).first()
        return annotator

    @staticmethod
    def create(annotator: api.Annotator,
               db_session: Session,
               commit=True) -> db.Annotator:
        """
        Create a new service in the database.
        """

        existing_annotator = db_session.exec(select(db.Annotator).where(and_(
            db.Annotator.name == annotator.name,
            db.Annotator.version == annotator.version,
        ))).first()
        if not existing_annotator:
            anno = db.Annotator.model_validate(annotator)
            db_session.add(anno)
            if commit:
                db_session.commit()
                db_session.refresh(anno)
            else:
                db_session.flush()
            return anno
        else:
            return existing_annotator
