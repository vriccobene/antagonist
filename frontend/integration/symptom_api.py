import uuid
import pandas as pd
import requests


symptom_data = [
    {
        "ID": "2fc901ba-c941-4dba-a3a6-94ca3618a24d", 
        "event-id": "b6dd9242-e600-4697-9360-77f92ddf2bb9", 
        "description": "Control Plane affected 01", 
        "start-time": "2024-01-12 08:26:49.219717", 
        "end-time": "2024-01-13 18:20:12.000124", 
        "confidence-score": 0.5, 
        "concern-score": 0.3, 
        "plane": "control", 
        "condition": "Test-XXX",
        "action": "Test-YYY", 
        "cause": "Test-ZZZ", 
        "pattern": "Mean shift", 
        "source-type": "algorithm", 
        "source-name": "AnomalyDetector-1",
        "tags": {
            "url": "XYZ",
            "metric_name": "BGP Flow Count"
        }
    },
    {
        "ID": "2fc901ba-c941-4dba-a3a6-94ca3618a24d", 
        "event-id": "b6dd9242-e600-4697-9360-77f92ddf2bb9", 
        "description": "Control Plane affected 02", 
        "start-time": "2024-01-14 08:26:49.219717", 
        "end-time": "2024-01-15 18:20:12.000124", 
        "confidence-score": 0.5, 
        "concern-score": 0.3, 
        "plane": "control", 
        "condition": "Test-XXX",
        "action": "Test-YYY", 
        "cause": "Test-ZZZ", 
        "pattern": "Mean shift", 
        "source-type": "algorithm", 
        "source-name": "AnomalyDetector-1",
        "tags": {
            "url": "XYZ",
            "metric_name": "BGP Flow Count"
        }
    },
    {
        "ID": "2fc901ba-c941-4dba-a3a6-94ca3618a24d", 
        "event-id": "b6dd9242-e600-4697-9360-77f92ddf2bb9", 
        "description": "Control Plane affected 03", 
        "start-time": "2024-01-16 08:26:49.219717", 
        "end-time": "2024-01-17 18:20:12.000124", 
        "confidence-score": 0.5, 
        "concern-score": 0.3, 
        "plane": "control", 
        "condition": "Test-XXX",
        "action": "Test-YYY", 
        "cause": "Test-ZZZ", 
        "pattern": "Mean shift", 
        "source-type": "algorithm", 
        "source-name": "AnomalyDetector-1",
        "tags": {
            "url": "XYZ",
            "metric_name": "BGP Flow Count"
        }
    },
    {
        "ID": "2fc901ba-c941-4dba-a3a6-94ca3618a24d", 
        "event-id": "b6dd9242-e600-4697-9360-77f92ddf2bb9", 
        "description": "Control Plane affected 04", 
        "start-time": "2024-01-18 08:26:49.219717", 
        "end-time": "2024-01-19 18:20:12.000124", 
        "confidence-score": 0.5, 
        "concern-score": 0.3, 
        "plane": "control", 
        "condition": "Test-XXX",
        "action": "Test-YYY", 
        "cause": "Test-ZZZ", 
        "pattern": "Mean shift", 
        "source-type": "algorithm", 
        "source-name": "AnomalyDetector-1",
        "tags": {
            "url": "XYZ",
            "metric_name": "BGP Flow Count"
        }
    },
]
column_subset = [
    "ID", "description", "start-time", "end-time", 
    "confidence-score", "concern-score"
]
column_fullset = [
    "ID", "event-id", "description", "start-time", "end-time", 
    "confidence-score", "concern-score", "plane", "condition", 
    "action", "cause", "pattern", "source-type", "source-name"]


def get_symptoms(
        subset=True, incident_id:str=None, symptom_id:str=None, 
        start_time=None, end_time=None):
    url = "http://localhost:5001/api/rest/v1/symptom"

    params = {
        "incident-id": incident_id,
        "symptom-id": symptom_id,
        "start-time": start_time,
        "end-time": end_time
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    symptom_data = response.json()
    
    # df = pd.DataFrame.from_dict(symptom_data)
    # filter_df = df.drop_duplicates(subset=columns)
    # filter_df = df[df.ID.isin(symptom_ids)] if symptom_ids else filter_df
    # print(filter_df)
    # return filter_df[columns].to_dict('records')
    return symptom_data


def get_symptoms_col_def(subset=True):
    columns = column_subset if subset else column_fullset
    column_defs = [{"field": columns[0], "checkboxSelection": True, "sortable": True, "filter": True}]
    column_defs.extend([{"field": field, "sortable": True, "filter": True} for field in columns[1:]])
    return column_defs


def get_symptom(symptom_id: uuid.UUID):
    return next(symptom for symptom in symptom_data if net_anomaly.get('ID') == symptom_data)
