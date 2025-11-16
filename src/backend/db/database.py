import os
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import create_engine
from sqlalchemy.orm import declarative_base


# Load the environment variables from the .env file
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DBNAME')

connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(connection_string)

Base = declarative_base()
