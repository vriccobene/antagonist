import uvicorn
import logging
from fastapi import FastAPI
from routers import (
    relevant_state, annotator, anomaly, service,
    data_source, monitored_entity_type, telemetry
)
from utils import logger
from fastapi.middleware.cors import CORSMiddleware


logger.configure_logging()
log = logging.getLogger(__name__)


app = FastAPI(root_path="/api/v1")
app.include_router(relevant_state.router,
                   prefix="/label-store/relevant-state")
app.include_router(annotator.router,
                   prefix="/label-store/annotator")
app.include_router(anomaly.router,
                   prefix="/label-store/anomaly")
app.include_router(service.router,
                   prefix="/label-store/service")
app.include_router(data_source.router,
                   prefix="/telemetry/data-source")
app.include_router(monitored_entity_type.router,
                   prefix="/telemetry/monitored-entity-type")
app.include_router(monitored_entity_type.router_existing_services,
                   prefix="/telemetry/router_existing_services")
app.include_router(telemetry.router,
                   prefix="/telemetry/data")


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Antagonist API", "version": "0.1.0"}


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # TODO - In production, specify actual origins
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def initialize_db():
    from sqlmodel import SQLModel
    from db.database import engine
    from data_models.label_store.db import (
        RelevantState, Symptom, Annotator,
        RelevantStateAnomalyLink, Anomaly,
        Publisher, Service
    )
    from data_models.telemetry.db import (
        DataSource, MonitoredEntityType
    )
    SQLModel.metadata.create_all(engine)


def main():
    initialize_db()
    log.info("Starting Antagonist Label Store")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


if __name__ == '__main__':
    main()
