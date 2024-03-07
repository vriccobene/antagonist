import requests


response = requests.post("http://localhost:5001/api/rest/v1/symptom")
if response.status_code == 200:
    network_anomalies = response.json()
    return _postprocess_network_anomalies(network_anomalies)
else:
    raise Exception("Failed to retrieve network anomalies from the API")


symptoms = [
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