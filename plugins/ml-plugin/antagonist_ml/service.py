import uuid
import datetime
import json
from typing import Dict, List, Union


def get_network_anomaly_labels(
    service_id: str,
    start_timestamp: int,
    end_timestamp: int,
    author_type: str,
    validation: bool = False,
) -> List[Dict]:
    """
    Retrieve Network Anomaly labels given the following input.
    - Service ID
    - Start timestamp
    - End timestamp
    - Author type [human, algorithm]
    - Validation [bool]: if True, the function will return the only labels that have been validated by a human.
    """
    pass


def get_network_symptoms_labels(
    service_id: str,
    start_timestamp: int,
    end_timestamp: int,
    author_type: str,
    network_anomaly: bool = False,
) -> List[Dict]:
    """
    Retrieve Network Symptoms labels given the following input.
    - Service ID
    - Start timestamp
    - End timestamp
    - Author type [human, algorithm]
    - Network Anomaly [bool]: if True, the function will return the only labels that have been associated to a Network Anomaly.
    """
    pass


def store_network_anomalies_labels(
    author_name: str,
    author_type: str,
    author_version: int,
    description: str,
    start: int,
    end: int,
    state: str = "incident-potential",
    version: int = 1,
) -> str:
    """
    Store network anomaly labels in a data structure.

    Args:
        author_name (str): The name of the author who created the label.
        author_type (str): The type of the author, either "algorithm" or "human".
        author_version (int): The version of the author.
        description (str): A description of the network anomaly.
        start (int): The start timestamp of the network anomaly.
        end (int): The end timestamp of the network anomaly.
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
        "start": datetime.datetime.fromtimestamp(start).strftime("%Y-%m-%dT%H:%M:%S"),
        "end": datetime.datetime.fromtimestamp(end).strftime("%Y-%m-%dT%H:%M:%S"),
        "id": network_anomaly_uuid,
        "state": state,
        "version": version,
    }

    print(json.dumps(net_inc))

    return network_anomaly_uuid


def store_network_symptom_labels(
    author_name: str,
    author_type: str,
    author_version: int,
    confidence: float,
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
        author_name (str): The name of the author who created the label.
        author_type (str): The type of the author, either "algorithm" or "human".
        author_version (int): The version of the author.
        confidence (float): The confidence score of the network symptom label.
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

    symptom_uuid = str(uuid.uuid4())
    event_uuid = str(uuid.uuid4())
    net_sym = {
        "confidence-score": confidence,
        "description": description,
        "start-time": datetime.datetime.fromtimestamp(start).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),
        "end-time": datetime.datetime.fromtimestamp(end).strftime("%Y-%m-%dT%H:%M:%S"),
        "event-id": event_uuid,
        "id": symptom_uuid,
        "source-name": f"{author_name}_{author_version}",
        "source-type": author_type,
        "tags": tags,
    }

    print(json.dumps(net_sym))

    if network_anomaly_uuid:
        sym_to_net = {"symptom-id": symptom_uuid, "incident-id": network_anomaly_uuid}
        print(json.dumps(sym_to_net))
