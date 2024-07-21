import uuid
import json
import pandas as pd
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


ANTAGONIST_CORE_HOST = "http://antagonist-core:5001"
# ANTAGONIST_CORE_HOST = "http://localhost:5001"


column_subset = [
    "id", "description", "start-time", "end-time", 
    "confidence-score", "concern-score", "url"
]
column_fullset = [
    "id", "event-id", "description", "start-time", "end-time", 
    "confidence-score", "concern-score", 
    # "plane", "condition", "action", "cause", 
    "pattern", "source-type", "source-name", "url"]


def get_symptoms(
        subset=True, network_anomaly_id:str=None, symptom_id:str=None, 
        start_time=None, end_time=None):
    url = f"{ANTAGONIST_CORE_HOST}/api/rest/v1/symptom"

    payload = json.dumps({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer eyJrIjoiZnVMc2pWeFkwNG81MmlxVUVJUWY2T20yblh6ZzkxUTEiLCJuIjoiYW50YWdvbmlzdCIsImlkIjoxfQ=="
    })

    headers = {
    'Authorization': 'Bearer glsa_jpNMmdn5d1lvuVbdc8f4cQ2Q0WTsAJbh_55df2413',
    'Content-Type': 'application/json'
    }

    params = {
        "network-anomaly-id": network_anomaly_id,
        "symptom-id": symptom_id,
        "start-time": start_time,
        "end-time": end_time
    }

    response = requests.request("GET", url, headers=headers, data=payload, params=params)

    # headers = {
    #     "Authorization": "Bearer glsa_jpNMmdn5d1lvuVbdc8f4cQ2Q0WTsAJbh_55df2413",
    #     "Content-Type": "application/json",
    #     "Accept": "application/json"
    # }
    # body = {
    #     "Content-Type": "application/json",
    #     "Accept": "application/json",
    #     # "Authorization": "Bearer eyJrIjoiZnVMc2pWeFkwNG81MmlxVUVJUWY2T20yblh6ZzkxUTEiLCJuIjoiYW50YWdvbmlzdCIsImlkIjoxfQ==",
    # }
    # params = {
    #     "network-anomaly-id": network_anomaly_id,
    #     "symptom-id": symptom_id,
    #     "start-time": start_time,
    #     "end-time": end_time
    # }

    # response = requests.get(url, headers=headers, params=params)

    logger.error(f"Parameters: {params}")
    logger.error(f"Response: {response.json()}")

    response.raise_for_status()
    symptom_data = response.json()
    
    # df = pd.DataFrame.from_dict(symptom_data)
    # filter_df = df.drop_duplicates(subset=columns)
    # filter_df = df[df.ID.isin(symptom_ids)] if symptom_ids else filter_df
    # print(filter_df)
    # return filter_df[columns].to_dict('records')
    
    return [_prepare_symptom_for_visualization(symptom) 
            for symptom in symptom_data]
    # return symptom_data


def _prepare_symptom_for_visualization(symptom: dict):
    res = dict()
    for k, v in symptom.items():
        if k == "tags":
            res["url"] = v.get("url")
        else:
            res[k] = v
    return res


def get_symptoms_col_def(subset=True):
    columns = column_subset if subset else column_fullset
    column_defs = [{"field": columns[0], "checkboxSelection": True, "sortable": True, "filter": True}]
    column_defs.extend([{"field": field, "sortable": True, "filter": True} for field in columns[1:]])
    
    for col in column_defs:
        if col['field'] == 'url':
            col['cellRenderer'] = "markdown"
            col["cellStyle"] = {'background-color': '#707070'}
    
    return column_defs


# def get_symptom(symptom_id: uuid.UUID):
#     return next(symptom for symptom in symptom_data if net_anomaly.get('ID') == symptom_data)
