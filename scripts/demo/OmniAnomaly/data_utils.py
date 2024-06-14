import copy
import requests
from grafana import auth_api, dashboard_api, annotation_api


def get_grafana_annotations(start_time, end_time):
    grafana_auth = auth_api.GrafanaAuthApi()
    grafana_annotations = annotation_api.GrafanaAnnotationApi(grafana_auth)
    annotations = grafana_annotations.get(start_time, end_time, limit=1000)
    return annotations


def get_network_anomalies():
    response = requests.get("http://localhost:5001/api/rest/v1/incident")
    response.raise_for_status()
    return response.json()


def get_symptoms():
    response = requests.get("http://localhost:5001/api/rest/v1/symptom")
    response.raise_for_status()
    return response.json()


def retrieve_data_from_db():
    data = {
        "grafana_annotations": get_grafana_annotations(1697755029685, 1897755105462),
        "network_anomalies": get_network_anomalies(),
        "symptoms": get_symptoms()
    }
    return data


def store_grafana_annotations(annotations):
    grafana_auth = auth_api.GrafanaAuthApi()
    grafana_annotations = annotation_api.GrafanaAnnotationApi(grafana_auth)
    # refined_annotations = [_refine_annotation(annotation) for annotation in annotations]
    # response = grafana_annotations.post(refined_annotations)
    res = list()
    for annotation in annotations:
        res.append(grafana_annotations.post(annotation))
    return res


def store_symptoms(symptom_json):
    res = dict()
    new_json = copy.deepcopy(symptom_json)
    for symptom in new_json:
        old_id = symptom.pop('id', None)
        response = requests.post("http://localhost:5001/api/rest/v1/symptom", json=symptom)
        print(response.json())
        print(symptom)
        response.raise_for_status()
        res[old_id] = response.json()
    return res


def store_network_anomalies(network_anomaly_json):
    res = dict()
    new_json = copy.deepcopy(network_anomaly_json)
    for network_anomaly in new_json:
        old_id = network_anomaly.pop('id', None)
        response = requests.post("http://localhost:5001/api/rest/v1/incident", json=network_anomaly)
        response.raise_for_status()
        res[old_id] = response.json()
    return res


def _refine_annotation(annotation:dict):
    return  { 
	    'dashboardUID': annotation.get('dashboardUID'), 
	    'panelId': annotation.get('panelId'), 
	    'time': annotation.get('time'), 
	    'timeEnd': annotation.get('timeEnd'), 
	    'text': annotation.get('text'), 
	    'tags': annotation.get('tags') 
    }


def store_symptoms_to_network_anomalies(symptoms_to_network_anomalies_json):
    response = requests.post("http://localhost:5001/api/rest/v1/incident/symptom", json=symptoms_to_network_anomalies_json)
    response.raise_for_status()
    return response.json()


def store_data_to_db(data_to_store):
    print(data_to_store['grafana_annotations'])


    store_grafana_annotations(data_to_store['grafana_annotations'])
    network_anomaly_ids_to_replace = store_network_anomalies(data_to_store['network_anomalies'])
    symptom_id_to_replace = store_symptoms(data_to_store['symptoms'])

    for item in data_to_store['symptoms-to-network-anomalies']:
        if item['incident-id'] in network_anomaly_ids_to_replace.keys():
            item['incident-id'] = network_anomaly_ids_to_replace[item['incident-id']]
        if item['symptom-id'] in symptom_id_to_replace.keys():
            item['symptom-id'] = symptom_id_to_replace[item['symptom-id']]

    store_symptoms_to_network_anomalies(data_to_store['symptoms-to-network-anomalies'])


def main():
    # data = retrieve_data_from_db()
    # print(data)
    data = {
        # 'grafana_annotations': [
        #     {'id': 7, 'alertId': 0, 'alertName': '', 'dashboardId': 2, 'dashboardUID': 'cd11474b-935b-4348-b6b0-622bf3adfdb3', 'panelId': 10, 'userId': 0, 'newState': '', 'prevState': '', 'created': 1710280063405, 'updated': 1710280063405, 'time': 1710275682664, 'timeEnd': 1710277074331, 'text': 'March 002', 'tags': ['Incident'], 'login': 'admin', 'email': 'admin@localhost', 'avatarUrl': '/grafana/avatar/46d229b033af06a191ff2267bca9ae56', 'data': {}}, 
        #     {'id': 2, 'alertId': 0, 'alertName': '', 'dashboardId': 1, 'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'userId': 0, 'newState': '', 'prevState': '', 'created': 1710279417763, 'updated': 1710279417763, 'time': 1710276601865, 'timeEnd': 1710276664293, 'text': '2 Drops of Reliability in the same sequence - 001', 'tags': ['Symptom'], 'login': 'admin', 'email': 'admin@localhost', 'avatarUrl': '/grafana/avatar/46d229b033af06a191ff2267bca9ae56', 'data': {}}, 
        #     {'id': 4, 'alertId': 0, 'alertName': '', 'dashboardId': 1, 'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'userId': 0, 'newState': '', 'prevState': '', 'created': 1710279493097, 'updated': 1710279493097, 'time': 1710275837555, 'timeEnd': 1710275840253, 'text': 'Spike of Output Load - 001', 'tags': ['Symptom'], 'login': 'admin', 'email': 'admin@localhost', 'avatarUrl': '/grafana/avatar/46d229b033af06a191ff2267bca9ae56', 'data': {}}, 
        #     {'id': 6, 'alertId': 0, 'alertName': '', 'dashboardId': 2, 'dashboardUID': 'cd11474b-935b-4348-b6b0-622bf3adfdb3', 'panelId': 10, 'userId': 0, 'newState': '', 'prevState': '', 'created': 1710280047242, 'updated': 1710280072577, 'time': 1710274131379, 'timeEnd': 1710275622807, 'text': 'March 001', 'tags': ['Incident'], 'login': 'admin', 'email': 'admin@localhost', 'avatarUrl': '/grafana/avatar/46d229b033af06a191ff2267bca9ae56', 'data': {}}, 
        #     {'id': 3, 'alertId': 0, 'alertName': '', 'dashboardId': 1, 'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'userId': 0, 'newState': '', 'prevState': '', 'created': 1710279435633, 'updated': 1710279435633, 'time': 1710275515473, 'timeEnd': 1710275518409, 'text': 'Little Drop of Reliability - 001', 'tags': [], 'login': 'admin', 'email': 'admin@localhost', 'avatarUrl': '/grafana/avatar/46d229b033af06a191ff2267bca9ae56', 'data': {}}, 
        #     {'id': 1, 'alertId': 0, 'alertName': '', 'dashboardId': 1, 'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'userId': 0, 'newState': '', 'prevState': '', 'created': 1710279387602, 'updated': 1710279387602, 'time': 1710274738845, 'timeEnd': 1710274743246, 'text': 'Drop of Reliability 001', 'tags': ['Symptom'], 'login': 'admin', 'email': 'admin@localhost', 'avatarUrl': '/grafana/avatar/46d229b033af06a191ff2267bca9ae56', 'data': {}}, 
        #     {'id': 5, 'alertId': 0, 'alertName': '', 'dashboardId': 1, 'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'userId': 0, 'newState': '', 'prevState': '', 'created': 1710279573609, 'updated': 1710279573609, 'time': 1710274182040, 'timeEnd': 1710274239544, 'text': 'Strange Shape of Byte sent', 'tags': ['Symptom'], 'login': 'admin', 'email': 'admin@localhost', 'avatarUrl': '/grafana/avatar/46d229b033af06a191ff2267bca9ae56', 'data': {}}
        # ],
        'grafana_annotations': [
            {'dashboardUID': 'cd11474b-935b-4348-b6b0-622bf3adfdb3', 'panelId': 10, 'time': 1710275682664, 'timeEnd': 1710277074331, 'text': 'March 002', 'tags': ['Incident']}, 
            {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710276601865, 'timeEnd': 1710276664293, 'text': '2 Drops of Reliability in the same sequence - 001', 'tags': ['Symptom']}, 
            {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710275837555, 'timeEnd': 1710275840253, 'text': 'Spike of Output Load - 001', 'tags': ['Symptom']}, 
            {'dashboardUID': 'cd11474b-935b-4348-b6b0-622bf3adfdb3', 'panelId': 10, 'time': 1710274131379, 'timeEnd': 1710275622807, 'text': 'March 001', 'tags': ['Incident']}, 
            {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710275515473, 'timeEnd': 1710275518409, 'text': 'Little Drop of Reliability - 001', 'tags': []}, 
            {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710274738845, 'timeEnd': 1710274743246, 'text': 'Drop of Reliability 001', 'tags': ['Symptom']}, 
            {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710274182040, 'timeEnd': 1710274239544, 'text': 'Strange Shape of Byte sent', 'tags': ['Symptom']}
        ],
        'network_anomalies': [
            {'author': {'author_type': 'human', 'name': 'admin', 'version': 0}, 'description': 'March 001', 'id': 'c5873775-0fba-4b97-81b5-bf3fc73dcd18', 'state': 'potential', 'version': 1},
            {'author': {'author_type': 'human', 'name': 'admin', 'version': 0}, 'description': 'March 002', 'id': '02fcd49c-f751-4f0d-b129-1b95a98ec6d4', 'state': 'potential', 'version': 1}, 
            {'author': {'author_type': 'person', 'name': 'admin', 'version': 0}, 'description': 'March 001', 'id': 'cefaffdb-d273-4e7a-9928-7b124734e066', 'state': 'potential', 'version': 2}, 
            {'author': {'author_type': 'person', 'name': 'admin', 'version': 0}, 'description': 'March 001', 'id': '57536c19-f458-4660-9763-6665166d903b', 'state': 'Confirmed', 'version': 3},
            {"author": {"author_type": "person", "name": "admin", "version": 0}, "description": "March 001", "id": "57536c19-f458-4660-9763-6665166d903b", "state": "Confirmed", "version": 3}
        ],
        'symptoms': [
            {'action': 'Reachability', 'cause': 'Peer Down', 'concern-score': 0.2, 'confidence-score': 1.0, 'description': '2 Drops of Reliability in the same sequence - 001', 'end-time': '2024-03-12T20:51:04', 'event-id': 'af152ac4-2984-44ac-946f-3c4cdd558f16', 'id': 'e1298c7d-b75a-4b7a-9f4a-f8216a8af6d3', 'pattern': 'drop', 'plane': 'control', 'reason': 'Withdraw', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:50:01', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710276535722&to=1710276752902&var-Resolution=1s&var-fields=reliability'}}, 
            {'action': 'Adjacency', 'cause': 'Administrative', 'concern-score': 0.8, 'confidence-score': 0.4, 'description': 'Spike of Output Load - 001', 'end-time': '2024-03-12T20:37:20', 'event-id': 'd4c4d2d4-07e3-42c8-856f-e2590523e956', 'id': '2a890c1d-2e22-4b00-9cf9-6c0cc2e5a1ef', 'pattern': 'spike', 'plane': 'control', 'reason': 'Locally Teared Down', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:37:17', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710275831584&to=1710275849390&var-Resolution=1s&var-fields=output-load'}}, 
            {'action': 'Missing', 'cause': 'Time', 'concern-score': 0.1, 'confidence-score': 0.1, 'description': 'Strange Shape of Byte sent', 'end-time': '2024-03-12T20:10:39', 'event-id': 'ce01514c-9780-4755-ae00-1c9f56223f4a', 'id': '822cedc1-aa29-4a13-92e5-0c401ef73b92', 'pattern': 'mean-shift', 'plane': 'forwarding', 'reason': 'Previous', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:09:42', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710274141546&to=1710274288347&var-Resolution=1s&var-fields=bytes-sent'}}, 
            {'action': 'Adjacency', 'cause': 'Link-Layer', 'concern-score': 0.7, 'confidence-score': 0.1, 'description': 'Drop of Reliability 001', 'end-time': '2024-03-12T20:19:03', 'event-id': '22873b20-8e0c-4fcf-b8d9-5334b66cd43d', 'id': '0625bd54-adb4-4227-941f-b0198bd3c227', 'pattern': 'drop', 'plane': 'control', 'reason': 'Established', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:18:58', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710274736690&to=1710274745711&var-Resolution=1s&var-fields=reliability'}}
        ],
        'symptoms-to-network-anomalies': [
            {"incident-id": "57536c19-f458-4660-9763-6665166d903b", "symptom-id": "e1298c7d-b75a-4b7a-9f4a-f8216a8af6d3"}, 
            {"incident-id": "57536c19-f458-4660-9763-6665166d903b", "symptom-id": "2a890c1d-2e22-4b00-9cf9-6c0cc2e5a1ef"}
        ]
    }
    store_data_to_db(data)


if __name__ == "__main__":
    main()
