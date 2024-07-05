import uuid
import requests
import pandas as pd

import logging
logger = logging.getLogger(__name__)


ANTAGONIST_CORE_HOST = "http://antagonist-core:5001"


column_subset = ["Description"]
column_fullset = ["ID", "Description", "Annotator Name", "Version", "State"]


def create_new_network_anomaly_version(network_anomaly_id: uuid.UUID, network_anomaly_record:dict, network_anomaly_symptoms:list):
    # Create the new network anomaly version
    logger.error(f"Invoking API on: {ANTAGONIST_CORE_HOST}")
    body = {
        "description": network_anomaly_record.get("Description"), 
        "version": network_anomaly_record.get("Version"), 
        "state": network_anomaly_record.get("State"), 
        "annotator": {
            "name": network_anomaly_record.get("Annotator Name"), 
            "annotator_type": "human"
        }
    }
    new_network_anomaly_id = requests.post(f"{ANTAGONIST_CORE_HOST}/api/rest/v1/network_anomaly", 
                                json=body)

    # Relate the new network anomaly to the indicated symptoms
    body = [{"network-anomaly-id": new_network_anomaly_id.json(), 
             "symptom-id": sym.get("id")} 
            for sym in network_anomaly_symptoms]
    response = requests.post(f"{ANTAGONIST_CORE_HOST}/api/rest/v1/network_anomaly/symptom", 
                             json=body)
    if response.status_code == 200:
        network_anomalies = response.json()
        return network_anomalies
    else:
        raise Exception("Failed to store relationship between network " \
                        "anomaly and symptoms in the API")


def _retrieve_network_anomalies():
    response = requests.get(f"{ANTAGONIST_CORE_HOST}/api/rest/v1/network_anomaly")
    if response.status_code == 200:
        network_anomalies = response.json()
        return _postprocess_network_anomalies(network_anomalies)
    else:
        logger.error(f"Response: {response}")
        raise Exception("Failed to retrieve network anomalies from the API")


def get_network_anomalies(subset=True, network_anomaly_description=None):
    network_anomalies = _retrieve_network_anomalies()
    if len(network_anomalies) == 0:
        return []
    columns = column_subset if subset else column_fullset
    df = pd.DataFrame.from_dict(network_anomalies)
    filter_df = df.drop_duplicates(subset=columns)
    filter_df = df[df.Description == network_anomaly_description
                   ] if network_anomaly_description else filter_df
    return filter_df[columns].to_dict('records')


def _postprocess_network_anomalies(net_anomalies:dict):
    res = list()
    for anomaly in net_anomalies:
        new_anomaly = dict()
        new_anomaly["ID"] = anomaly["id"]
        new_anomaly["Description"] = anomaly["description"]
        new_anomaly["Version"] = anomaly["version"]
        new_anomaly["State"] = anomaly["state"]
        new_anomaly["Annotator Name"] = anomaly["annotator"]["name"]
        res.append(new_anomaly)
    return res


def get_network_anomaly_col_def(subset=True):
    columns = column_subset if subset else column_fullset
    column_defs = [{"field": columns[0], "checkboxSelection": True, "sortable": True, "filter": True}]
    column_defs.extend([{"field": field, "sortable": True, "filter": True} for field in columns[1:]])
    return column_defs


# def get_network_anomaly(network_anomaly_id: uuid.UUID):
#     # TODO Replace with call to the API
#     return next(net_anomaly for net_anomaly in network_anomaly_data if net_anomaly.get('ID') == network_anomaly_data)
