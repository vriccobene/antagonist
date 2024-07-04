import uuid
import time
import json
import requests
import datetime
import requests
from typing import Dict, List, Union


def get_network_anomaly_labels(
    antagonist_host: str,
    author_type: str = None,
    validation: bool = False,
) -> List[Dict]:
    """
    Retrieve Network Anomaly labels from the Antagonist service given the following input:
    
    Args:
        antagonist_host (str): The hostname of the Antagonist service.
        author_type (str, optional): The author type to filter the network anomaly labels by.
        validation (bool, optional): Whether to only return confirmed, analyzed, or adjusted network anomaly labels.
    
    Returns:
        List[Dict]: A list of network anomaly labels that match the provided filters.
    """
    response = requests.get(f"http://{antagonist_host}/api/rest/v1/incident")

    response.raise_for_status()
    response_json = response.json()

    return [
        net_anomaly
        for net_anomaly in response_json
        if (
            net_anomaly["state"].lower() in ["confirmed", "analysed", "adjusted"]
            or not validation
        )
        and (author_type is None or net_anomaly["author"]["author_type"] == author_type)
    ]


def get_network_symptoms_labels(
    antagonist_host: str,
    start_timestamp: int,
    end_timestamp: int,
    source_type: str = None,
    tags: Dict = None,
) -> List[Dict]:
    """
    Retrieve Network Symptoms labels given the following input.
    
    Args:
        antagonist_host (str): The hostname or IP address of the Antagonist service.
        start_timestamp (int): The start timestamp (in seconds) of the time range to filter the network symptoms by.
        end_timestamp (int): The end timestamp (in seconds) of the time range to filter the network symptoms by.
        source_type (str, optional): The source type to filter the network symptoms by.
        tags (Dict, optional): A dictionary of tags to filter the network symptoms by.
    
    Returns:
        List[Dict]: A list of network symptoms labels that match the provided filters.
    """

    response = requests.get(f"http://{antagonist_host}/api/rest/v1/symptom")
    response.raise_for_status()
    response_json = response.json()

    retrieve = []
    for symptom in response_json:
        start_time = datetime.datetime.strptime(symptom['start-time'], '%a, %d %b %Y %H:%M:%S %Z').timestamp()
        end_time = datetime.datetime.strptime(symptom['end-time'], '%a, %d %b %Y %H:%M:%S %Z').timestamp()

        # verify overlap between symptom interval and filters one
        time_overlap = (start_timestamp <= start_time <= end_timestamp) or (start_timestamp <= end_time <= end_timestamp)

        if (source_type is None or symptom["source-type"] == source_type) and time_overlap:
            if tags is None or all([symptom["tags"][tag] == tags[tag] for tag in tags]):
                symptom.update({
                    "start-time": start_time,
                    "end-time": end_time
                })
                retrieve.append(symptom)

    return retrieve


def store_network_anomalies_labels(
    antagonist_host: str,
    author_name: str,
    author_type: str,
    author_version: int,
    description: str,
    state: str = "incident-potential",
    version: int = 1,
) -> str:
    """
    Store network anomaly labels in a data structure.

    Args:
        antagonist_host (str): The hostname or IP address of the Antagonist service.
        author_name (str): The name of the author who created the label.
        author_type (str): The type of the author, either "algorithm" or "human".
        author_version (int): The version of the author.
        description (str): A description of the network anomaly.
        state (str, optional): The state of the network anomaly. Defaults to "incident-potential".
        version (int, optional): The version of the network anomaly label. Defaults to 1.

    Returns:
        str: The UUID of the stored network anomaly label.
    """
    assert author_type in ["algorithm", "human"]
    assert state in [
        "incident-forecasted",
        "incident-potential",
        "incident-confirmed",
        "discarded",
        "analysed",
        "adjusted",
    ]
    assert author_version > 0
    assert version > 0

    # generate uuid
    network_anomaly_uuid = str(uuid.uuid4())

    net_inc = {
        "author": {
            "author_type": author_type,
            "name": author_name,
            "version": author_version,
        },
        "description": description,
        "state": state,
        "version": version,
    }

    response = requests.post(
        f"http://{antagonist_host}/api/rest/v1/incident", json=net_inc
    )
    response.raise_for_status()
    network_anomaly_uuid = response.json()

    return network_anomaly_uuid


def store_network_symptom_labels(
    antagonist_host: str,
    author_name: str,
    author_type: str,
    author_version: int,
    confidence: float,
    concern_score: float,
    description: str,
    start: int,
    end: int,
    version: int = 1,
    tags: Dict[str, str] = {},
    network_anomaly_uuid: str = None,
):
    """
    Store network symptom labels in a data structure.

    Args:
        antagonist_host (str): The hostname or IP address of the Antagonist service.
        author_name (str): The name of the author who created the label.
        author_type (str): The type of the author, either "algorithm" or "human".
        concern_score (float): The concern score of the network symptom.
        description (str): A description of the network symptom.
        start (int): The start timestamp of the network symptom.
        end (int): The end timestamp of the network symptom.
        version (int, optional): The version of the network symptom label. Defaults to 1.
        tags (Dict[str, str], optional): A dictionary of tags associated with the network symptom label. Defaults to {}.
        network_anomaly_uuid (str, optional): The UUID of the associated network anomaly label. Defaults to None.

    Returns:
        None
    """
    assert author_type in ["algorithm", "human"]
    assert author_version > 0
    assert version > 0

    event_uuid = str(uuid.uuid4())
    net_sym = {
        "start-time": datetime.datetime.fromtimestamp(start).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),
        "end-time": datetime.datetime.fromtimestamp(end).strftime("%Y-%m-%dT%H:%M:%S"),
        "event-id": event_uuid,
        "concern-score": concern_score,
        "confidence-score": confidence,
        "description": description,
        "source-name": f"{author_name}_{author_version}",
        "source-type": author_type,
        "tags": tags,
        "action": "drop",
        "cause": "x",
        "reason": "{metric}",
        "plane": "forwarding",
        "pattern": "",
    }

    response = requests.post(
        f"http://{antagonist_host}/api/rest/v1/symptom", json=net_sym
    )
    response.raise_for_status()
    symptom_uuid = response.json()

    if network_anomaly_uuid:
        sym_to_net = {"symptom-id": symptom_uuid, "incident-id": network_anomaly_uuid}
        response = requests.post(
            f"http://{antagonist_host}/api/rest/v1/incident/symptom", json=sym_to_net
        )
        response.raise_for_status()


if __name__ == "__main__":
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365)
    get_network_symptoms_labels(
        "localhost:5001",
        source_type="human",
        start_timestamp=start.timestamp(),
        end_timestamp=end.timestamp(),
        tags={"machine": "machine-1-1"},
    )
