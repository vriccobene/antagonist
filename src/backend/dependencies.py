from sqlmodel import Session
from db.database import engine


def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
