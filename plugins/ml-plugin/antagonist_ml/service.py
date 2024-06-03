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


def store_network_symptoms_and_anomalies(data: Union[Dict, List]) -> None:
    """
    Store Network Symptoms and Network Anomalies in Antagonist.
    """
    pass
