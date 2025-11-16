import psycopg2
from sqlmodel import Session, select
from data_models.label_store import db, api


class SymptomView:

    @staticmethod
    def create(symptom: api.Symptom, db_session: Session) -> db.Symptom:
        """
        Create a new service in the database.
        """
        # TODO - Do I need to deal with duplicates?
        # existing_symptom = db_session.exec(select(Symptom).where(
        #     Symptom.id == symptom.id,
        # )).first()
        # if not existing_symptom:
        res = db.Symptom.model_validate(symptom)
        known_fields = set(api.Symptom.model_fields.keys())
        extra_fields = {k: v for k, v in dict(symptom).items()
                        if k not in known_fields}
        if extra_fields:
            res.data = extra_fields
        db_session.add(res)
        db_session.commit()
        db_session.refresh(res)
        return res
        # else:
        #     return existing_symptom
