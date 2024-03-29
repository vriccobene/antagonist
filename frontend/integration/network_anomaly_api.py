import uuid
import requests
import pandas as pd

import logging
logger = logging.getLogger(__name__)



ANTAGONIST_CORE_HOST = "http://antagonist-core:5001"

# network_anomaly_data = [
#     {"ID": "6ff58573-c1a1-4dc7-ab55-7b7f346d1070", "Description": "January 2023 - 01", "Author Name": "Vince", "Version": 1, "State": "Forecasted"},
#     {"ID": "a500d322-7dae-43fe-b4d9-51e1791e6b39", "Description": "March 2023 - 01", "Author Name": "Antonio", "Version": 1, "State": "Potential"},
#     {"ID": "a500d322-7dae-43fe-b4d9-51e1791e6b39", "Description": "March 2023 - 01", "Author Name": "Wanting", "Version": 2, "State": "Confirmed"},
#     {"ID": "7573b20a-5420-4750-8ee2-3caf87c2a860", "Description": "April 2023 - 01", "Author Name": "Thomas", "Version": 1, "State": "Confirmed"},
#     {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Vince", "Version": 1, "State": "Potential"},
#     {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Wanting", "Version": 2, "State": "Potential"},
#     {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Wanting", "Version": 3, "State": "Potential"},
#     {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Vince", "Version": 4, "State": "Discarded"},
#     {"ID": "1154face-711b-44b8-81cc-28032383c584", "Description": "November 2023 - 01", "Author Name": "Alex", "Version": 1, "State": "Confirmed"}
# ]

# post_requests = [
#     {"description": "January 2023 - 01", "version": 1, "state": "Forecasted", "author": {"name": "Vince", "author_type": "person"}},
#     {"description": "March 2023 - 01", "version": 1, "state": "Potential", "author": {"name": "Antonio", "author_type": "person"}},
#     {"description": "March 2023 - 01", "version": 2, "state": "Confirmed", "author": {"name": "Wanting", "author_type": "person"}},
#     {"description": "April 2023 - 01", "version": 1, "state": "Confirmed", "author": {"name": "Vince", "author_type": "person"}},
#     {"description": "September 2023 - 01", "version": 1, "state": "Potential", "author": {"name": "Thomas", "author_type": "person"}},
#     {"description": "September 2023 - 01", "version": 2, "state": "Potential", "author": {"name": "Wanting", "author_type": "person"}},
#     {"description": "September 2023 - 01", "version": 3, "state": "Potential", "author": {"name": "Wanting", "author_type": "person"}},
#     {"description": "September 2023 - 01", "version": 4, "state": "Discarded", "author": {"name": "Vince", "author_type": "person"}},
#     {"description": "November 2023 - 01", "version": 1, "state": "Confirmed", "author": {"name": "Alex", "author_type": "person"}}
# ]

column_subset = ["Description"]
column_fullset = ["ID", "Description", "Author Name", "Version", "State"]


def create_new_network_anomaly_version(network_anomaly_id: uuid.UUID, network_anomaly_record:dict, network_anomaly_symptoms:list):
    # Create the new network anomaly version
    logger.error(f"Invoking API on: {ANTAGONIST_CORE_HOST}")
    body = {
        "description": network_anomaly_record.get("Description"), 
        "version": network_anomaly_record.get("Version"), 
        "state": network_anomaly_record.get("State"), 
        "author": {
            "name": network_anomaly_record.get("Author Name"), 
            "author_type": "person"}
    }
    new_network_anomaly_id = requests.post(f"{ANTAGONIST_CORE_HOST}/api/rest/v1/incident", 
                                json=body)

    # Relate the new network anomaly to the indicated symptoms
    body = [{"incident-id": new_network_anomaly_id.json(), 
             "symptom-id": sym.get("id")} 
            for sym in network_anomaly_symptoms]
    response = requests.post(f"{ANTAGONIST_CORE_HOST}/api/rest/v1/incident/symptom", 
                             json=body)
    if response.status_code == 200:
        network_anomalies = response.json()
        return network_anomalies
    else:
        raise Exception("Failed to store relationship between network " \
                        "anomaly and symptoms in the API")


def _retrieve_network_anomalies():
    response = requests.get(f"{ANTAGONIST_CORE_HOST}/api/rest/v1/incident")
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
        new_anomaly["Author Name"] = anomaly["author"]["name"]
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
