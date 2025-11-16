from typing import List
from sqlmodel import Session, select, and_
from data_models.label_store import db, api


class PublisherView:

    @staticmethod
    def retrieve(publisher_id: str | None = None, db_session: Session = None) -> db.Publisher | List[db.Publisher]:
        """
        Retrieve a publisher by its ID or all publishers if no ID is provided.
        """
        if not publisher_id:
            statement = select(db.Publisher)
            publishers = db_session.exec(statement).all()
            return publishers
        statement = select(db.Publisher).where(db.Publisher.id == publisher_id)
        publisher = db_session.exec(statement).first()
        return publisher

    @staticmethod
    def create(
        publisher: api.Publisher,
        db_session: Session,
        commit=True) \
            -> db.Publisher:

        """
        Create a new publisher in the database.
        """

        statement = select(db.Publisher)
        statement = statement.where(db.Publisher.name == publisher.name)
        statement = statement.where(db.Publisher.version == publisher.version)
        existing_publisher = db_session.exec(statement).first()

        if not existing_publisher:
            pub = db.Publisher.model_validate(publisher)
            db_session.add(pub)
            if commit:
                db_session.commit()
                db_session.refresh(pub)
            else:
                db_session.flush()
            return pub
        else:
            return existing_publisher
