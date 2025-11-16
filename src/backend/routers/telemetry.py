from typing import List
from sqlmodel import Session
from fastapi import status, Depends, APIRouter

import dependencies
from data_models.label_store import api, api_request
from data_models.telemetry import api_request as telemetry_api_request
from views.relevant_state_view import RelevantStateView
from telemetry_integrations.telemetry_integration import TelemetryIntegration
from views import monitored_entity_type_view


router = APIRouter(tags=["telemetry"])


@router.get(
        '/relevant-state/{id}',
        response_model=api.RelevantState | List[api.RelevantState],
        status_code=status.HTTP_200_OK)
async def get(
        relevant_state_request: api_request.RelevantStateRequest = Depends(),
        start_time: str | None = None,
        end_time: str | None = None,
        db_session: Session = Depends(dependencies.get_session)):

    from datetime import datetime
    
    relevant_state_request = api_request.RelevantStateRequest(
        id=relevant_state_request.id)
    relevant_state = RelevantStateView.retrieve(
        relevant_state_request, db_session)
    if not relevant_state:
        return None

    anomalies = relevant_state.anomaly
    service = relevant_state.service

    monitored_entity_type = \
        monitored_entity_type_view.MonitoredEntityTypeView.retrieve(
            monitored_entity_type_request=telemetry_api_request.
            MonitoredEntityTypeRequest(name=service.type),
            db_session=db_session)

    updated_anomalies = list()
    for item in range(len(anomalies)):
        anomaly = anomalies[item].to_api_model()

        # Only fetch telemetry if monitored_entity_type and data_source exist
        if monitored_entity_type and monitored_entity_type.data_source:
            data_source = monitored_entity_type.data_source
            telemetry = TelemetryIntegration(data_source)
            
            # If start_time and end_time are provided, override the
            # anomaly times for telemetry data fetching
            if start_time and end_time:
                try:
                    # Parse the provided time range
                    override_start = datetime.fromisoformat(
                        start_time.replace('Z', '+00:00'))
                    override_end = datetime.fromisoformat(
                        end_time.replace('Z', '+00:00'))
                    
                    # Create temporary anomaly with extended time range
                    class ExtendedAnomaly:
                        def __init__(self, original_anomaly, start, end):
                            # Copy all attributes from original
                            for attr in dir(original_anomaly):
                                if not attr.startswith('_'):
                                    setattr(
                                        self, attr,
                                        getattr(original_anomaly, attr))
                            # Override the time range
                            self.start_time = start
                            self.end_time = end
                    
                    extended_anomaly = ExtendedAnomaly(
                        anomaly, override_start, override_end)
                    anomaly.telemetry_data = \
                        telemetry.get_anomaly_data(
                            extended_anomaly, service.type)
                except (ValueError, AttributeError) as e:
                    # If parsing fails, fall back to default behavior
                    print(f"Warning: Failed to parse time range "
                          f"parameters: {e}")
                    anomaly.telemetry_data = \
                        telemetry.get_anomaly_data(anomaly, service.type)
            else:
                # Use the anomaly's own time range
                anomaly.telemetry_data = \
                    telemetry.get_anomaly_data(anomaly, service.type)

        updated_anomalies.append(anomaly)

    db_session.close()
    relevant_state = relevant_state.to_api_model()
    relevant_state.anomaly = updated_anomalies
    return relevant_state


@router.get(
        '/query',
        status_code=status.HTTP_200_OK)
async def query_telemetry(
        service_type: str,
        metric: str,
        dimensions: str,
        start_time: str,
        end_time: str,
        db_session: Session = Depends(dependencies.get_session)):
    """
    Query telemetry data for a specific metric and dimensions.
    Dimensions should be passed as a JSON string.
    Example: /query?service_type=machine&metric=disk_usage&
    dimensions={"host":"server1"}&start_time=...&end_time=...
    """
    import json
    from datetime import datetime

    # Parse dimensions from JSON string
    try:
        dimensions_dict = json.loads(dimensions)
    except json.JSONDecodeError as e:
        db_session.close()
        return {
            "error": "Invalid dimensions format. Must be valid JSON.",
            "details": str(e)
        }

    # Parse datetime strings
    try:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    except ValueError as e:
        db_session.close()
        return {
            "error": "Invalid datetime format. Use ISO format.",
            "details": str(e)
        }

    # Get monitored entity type to find data source
    monitored_entity_type = \
        monitored_entity_type_view.MonitoredEntityTypeView.retrieve(
            monitored_entity_type_request=telemetry_api_request.
            MonitoredEntityTypeRequest(name=service_type),
            db_session=db_session)

    if not monitored_entity_type or not monitored_entity_type.data_source:
        db_session.close()
        return {"error": "No data source configured for this service type"}

    # Create a temporary symptom-like object for the query
    class TempSymptom:
        def __init__(self, metric, dimensions):
            self.metric = metric
            self.dimensions = dimensions

    class TempAnomaly:
        def __init__(self, metric, dimensions, start_time, end_time):
            self.symptom = TempSymptom(metric, dimensions)
            self.start_time = start_time
            self.end_time = end_time

    temp_anomaly = TempAnomaly(metric, dimensions_dict, start_dt, end_dt)

    # Fetch telemetry data
    try:
        data_source = monitored_entity_type.data_source
        telemetry = TelemetryIntegration(data_source)
        telemetry_data = telemetry.get_anomaly_data(
            temp_anomaly, service_type)

        db_session.close()
        return {"telemetry_data": telemetry_data}
    except Exception as e:
        db_session.close()
        return {
            "error": "Failed to fetch telemetry data",
            "details": str(e)
        }
