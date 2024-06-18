import uuid
import time
import math
import pathlib
import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
# from grafana import dashboard_api
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

import data_utils

# InfluxDB configuration
INFLUX_ORG = 'ietf'
INFLUX_PORT = '8086'
INFLUX_HOST = 'localhost'
INFLUX_BUCKET = 'anomaly_detection'
INFLUX_TOKEN = 'qT83QJVt1wENkP3s8Lfgyw0A5mGMQ5NFDApl5xOYKC3B_7tM5eVm8G0cnUsCzEG_8J3YEk0o2i6oH6L9masMxA=='


DEMO_DATA_DIRECTORY = pathlib.Path(".") \
        / "data" / "OmniAnomaly" / "ServerMachineDataset"
DATA_TEST_SET = DEMO_DATA_DIRECTORY / "test"
DATA_TRAINING_SET = DEMO_DATA_DIRECTORY / "train"
DATA_LABELS = DEMO_DATA_DIRECTORY / "interpretation_label"


existing_dashboards = dict()


def metric_names(indexes: list = None) -> list:
    names = [
        "cpu_r", "load_1", "load_5", "load_15", "mem_shmem", "mem_u",
        "mem_u_e", "total_mem", "disk_q", "disk_r", "disk_rb", "disk_svc", 
        "disk_u", "disk_w", "disk_wa", "disk_wb", "si", "so", "eth1_fi",
        "eth1_fo", "eth1_pi", "eth1_po", "tcp_tw", "tcp_use", "active_opens",
        "curr_estab", "in_errs", "in_segs", "listen_overflows", "out_rsts",
        "out_segs", "passive_opens", "retransegs", "tcp_timeouts", "udp_in_dg",
        "udp_out_dg", "udp_rcv_buf_errs", "udp_snd_buf_errs"]
    
    indexes = indexes or range(len(names))
    names = [names[i] for i in indexes]
    return names


def get_group_from_machine(machine_file_name: str) -> str:
    return f"Group-{machine_file_name.split('-')[1]}"


def load_data(data_dir: pathlib.Path) -> pd.DataFrame:
    """
    Given a directory containing the telemetry data, 
    this function loads the data in memory.
    """
    res = dict()
    for fle in data_dir.iterdir():
        machine = fle.name.replace(".txt", "")
        data_file = data_dir / fle.name

        group = get_group_from_machine(machine)
        res[group] = res.get(group, dict())
        res[group][machine] = pd.read_csv(data_file, sep=",", header=None, names=metric_names())
        
    return res


def format_time(epoch_time: int) -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(epoch_time))


def create_symptom_grafana_annotation(start_time: int, end_time: int, description: str, tags: list, dashboard_id:str=None) -> dict:
    """
    Create a symptom annotation in Grafana format

    :param start_time: The start time of the annotation (in milliseconds)
    :type start_time: int
    :param end_time: The end time of the annotation (in milliseconds)
    :type end_time: int
    :param description: The description of the symptom
    :type description: str
    
    :return: A dictionary representing the symptom annotation in Grafana format
    :rtype: dict
    """
    dashboard_id = dashboard_id or 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b'
    tags = tags or []
    symptom_grafana_annotation = {
        'dashboardUID': dashboard_id, 
        'panelId': 2, 
        'time': int(f'{start_time}000'), 
        'timeEnd': int(f'{end_time}000'), 
        'text': description, 
        'tags': tags + ['Symptom']
    }
    return symptom_grafana_annotation
    

def create_network_anomaly_grafana_annotation(start_time: int, end_time: int, description: str) -> dict:
    """
    Create a network anomaly annotation in Grafana format
    
    :param start_time: The start time of the network anomaly in epoch format.
    :type start_time: int
    :param end_time: The end time of the network anomaly in epoch format.
    :type end_time: int
    :param description: The description of the network anomaly.
    :type description: str
    
    :return: A dictionary representing the network anomaly annotation in Grafana format.
    :rtype: dict
    """
    return {
        'dashboardUID': 'cd11474b-935b-4348-b6b0-622bf3adfdb3', 
        'panelId': 10, 
        'time': int(f'{start_time}000'), 
        'timeEnd': int(f'{end_time}000'), 
        'text': description, 
        'tags': ['Incident']
    }


def define_symptom(group, machine, start_time, end_time, event_id, metric, description):
    return {
        'start-time': format_time(start_time),
        'end-time': format_time(end_time),
        'event-id': event_id, 
        'concern-score': 0.9, 
        'confidence-score': 1, 
        'description': description, 
        'source-name': 'ground-truth', 'source-type': 'human', 
        'action': 'drop', 'cause': 'x', 'reason': '{metric}', 'plane': 'forwarding', 'pattern': '', 
        'tags': {
            'machine': machine,
            'group': group,
            'metric': metric
        }
    }


def define_network_anomaly(machine, timestamp):
    return { 
        'author': {'author_type': 'human', 'name': 'admin', 'version': 0}, 
        'description': f'Network Anomaly on {machine} - {datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d at %H")}', 
        'state': 'Confirmed', 
        'version': 2,
        'symptoms': []
    }


def convert_labels_to_antagonist_format(data):
    res = {
        'grafana_annotations': [],
        'network_anomalies': [],
        'symptoms': [],
        'symptoms-to-network-anomalies': []
    }

    res = {'network_anomalies': []}
    for group, machine_labels in data.items():
        for machine in machine_labels:
            for label in machine_labels[machine]:
                timestamp = label['rows'][0]
                network_anomaly = define_network_anomaly(machine, timestamp)

                event_id = str(uuid.uuid4())
                for metric in label['columns']:
                    description = f'Symptom on {metric} of {machine}'
                    symptom = define_symptom(
                        group, machine, label["rows"][0], label["rows"][1], 
                        event_id, metric, description
                    )
                    network_anomaly['symptoms'].append(symptom)
                res['network_anomalies'].append(network_anomaly)

    return res


def load_labels(demo_data_labels: pathlib.Path) -> pd.DataFrame:
    """
    Given a directory containing the labels of the telemetry data,
    this function loads the labels in memory.
    """
    res = dict()
    for fle in demo_data_labels.iterdir():
        machine = fle.name.replace(".txt", "")
        lines = fle.read_text().split('\n')
        res[machine] = res.get(machine, list())
        for line in lines:
            anomaly = line.split(':')
            if len(anomaly) == 1:
                break
            res[machine].append({
                "rows": anomaly[0].split("-"),
                "columns": metric_names([int(m)-1 for m in anomaly[1].split(',')])
                # "columns": metric_names()[[int(m)-1 for m in anomaly[1]]]
            })

    return res


def explore_and_visualize_telemetry_data():
    test_data = load_data(DATA_TEST_SET)
    metric_ids = [1, 9, 10, 12, 13, 14, 15]
    metric_ids = [m - 1 for m in metric_ids]
    test_data = test_data.iloc[:, metric_ids]
    for metric in test_data.columns:
        test_data[metric].plot()
        plt.axvline(x = 15849, color = 'r', label = 'axvline - full height')
        plt.axvline(x = 16368, color = 'r', label = 'axvline - full height')
        plt.show()


def load_data_on_influx(data: pd.DataFrame, measurement: str, fields: dict = None) -> None:
    """
    Upload data on InfluxDB
    """
    fields = fields or dict()
    fields_str = f"{fields}"
    fields_str = fields_str.replace("{", "").replace("}", "").replace("'", "").replace(".txt", "").replace(":", "=").replace(" ", "")

    # Connect to DB
    client = InfluxDBClient(url=f'http://{INFLUX_HOST}:{INFLUX_PORT}', token=INFLUX_TOKEN)
    influx_api = client.write_api(write_opton=SYNCHRONOUS)

    step = 250
    start, end = 0, step
    while end < len(data):
        points = []
        for index, row in data[start: end].iterrows():
            for col in row.index:
                # Do not store categorical metrics
                if isinstance(row[col], str):
                    continue
                # Skip nan values
                if row[col] == 'NaN' or math.isnan(row[col]):
                    continue
                field = f'{col}="{row[col]}"' if isinstance(row[col], str) else f'{col}={row[col]}'
                points.append(f"{measurement},omnids=1,{fields_str} {field} {index}000000000")

        influx_api.write(INFLUX_BUCKET, INFLUX_ORG, points)
        time.sleep(0.2)
        start, end = end, end + step
        print(f"DF [{start}: {end}] - points: {len(points)}")
        points = list()


def store_dataframe(data: pd.DataFrame, group: str, machine: str, end_time: int=0) -> None:
    nbr_sec_per_interval = 60

    # Refine timestamps of the data
    end = end_time or int(time.time())
    start = end - (int(len(data) * nbr_sec_per_interval))

    data['time'] = [int(val) for val in range(int(start), int(end), nbr_sec_per_interval)]
    print(f"Time window - Start: {data['time'].min()} - End: {data['time'].max()}")
    data.set_index('time', inplace=True)

    # # Add training data and test data to influxDB
    load_data_on_influx(
        data, "ServerMachineDataset", 
        fields={"group": group, "machine": machine})


def adjust_labels_timestamps(labels, now, overall_data_len, test_data):
    """
    Change the timestamps here, before sending them to the next step
    """

    res = dict()
    for group, machine_data in overall_data_len.items():
        res[group] = res.get(group, dict())
        for machine, data_len in machine_data.items():
            res[group][machine] = res[group].get(machine, list())
            if machine not in labels:
                continue
            for label in labels[machine]:
                test_data_len = len(test_data[group][machine])
                res[group][machine].append({
                    "rows": [now - ((test_data_len - int(row)) * 60) for row in label["rows"]],
                    # "rows": [now - (data_len * 60) + int(row) * 60 for row in label["rows"]],
                    "columns": label["columns"]
                })

    return res


def create_dashboard(label, dashboard_name, annotation_tags, dashboard_id):
    pass
    # api = dashboard_api.GrafanaDashboardApi()
    # path = pathlib.Path(__file__).parent.resolve()
    # with open(f"{path}/Symptom Tagging-20240611.json", "r") as dashboard_file:
    #     f_content = dashboard_file.read()
    #     f_content = f_content.replace("#METRIC_NAME_HERE", str(label['tags']['metric']))
    #     f_content = f_content.replace("#DASHBOARD_NAME_HERE", str(dashboard_name))
    #     f_content = f_content.replace("#ANNOTATION_TAGS_HERE", str(annotation_tags).replace('"', '').replace("'", '"'))
    #     f_content = f_content.replace("#DASHBOARD_ID_HERE", str(dashboard_id))
    #     f_content = f_content.replace("#MACHINE_NAME_HERE", str(label['tags']['machine']))
        
    #     dashboard_template = json.loads(f_content)
    #     api.create(dashboard_template)


# def generate_grafana_dashboard(label, start_time, stop_time):
#     dashboard_name = f"{label['tags']['machine']} - {label['tags']['metric']}"
#     tag_machine = label['tags']['machine']
#     tag_group = label['tags']['group']
#     tag_metric = label['tags']['metric']
#     combined_tag = f"{tag_group}-{tag_machine}-{tag_metric}"
#     annotation_tags = [
#         f"machine:{tag_machine}", 
#         f"group:{tag_group}", 
#         f"metric:{tag_metric}"
#     ]
    
#     dashboard_id = existing_dashboards.get(combined_tag, None)
#     if not dashboard_id:
#         dashboard_id = uuid.uuid4()
#         create_dashboard(label, dashboard_name, annotation_tags, dashboard_id)
#         existing_dashboards[combined_tag] = dashboard_id
#     url = f"http://localhost:3000/grafana/d/{dashboard_id}/orgId=1&from={start_time}&to={stop_time}&var-Resolution=1m&var-fields={label['tags']['metric']}"
#     return str(dashboard_id), url


def store_data_to_db(data_to_store):
    # Store the data in Antagonist
    for network_anomaly in data_to_store['network_anomalies']:
        network_anomaly_data = network_anomaly.copy()
        symptoms = network_anomaly_data.pop('symptoms')
        response = requests.post("http://localhost:5001/api/rest/v1/incident", json=network_anomaly_data)
        response.raise_for_status()
        network_anomaly_id = response.json()
    
        # Store Symptoms
        for symptom in symptoms:
            response = requests.post("http://localhost:5001/api/rest/v1/symptom", json=symptom)
            response.raise_for_status()
            symptom_id = response.json()
        
            # Store Symptoms to Network Anomalies
            symmptom_to_network_anomaly = {"incident-id": network_anomaly_id, "symptom-id": symptom_id}
            response = requests.post(
                "http://localhost:5001/api/rest/v1/incident/symptom", json=symmptom_to_network_anomaly)
            response.raise_for_status()


def main():
    # explore_and_visualize_telemetry_data()
    training_data = load_data(DATA_TRAINING_SET)
    test_data = load_data(DATA_TEST_SET)
    
    # Merge training and test data
    overall_data = dict()
    overall_data_len = dict()
    for group in training_data.keys():
        overall_data[group] = overall_data.get(group, dict())
        overall_data_len[group] = overall_data_len.get(group, dict())
        for machine in training_data[group].keys():
            overall_data[group][machine] = pd.concat([training_data[group][machine], test_data[group][machine]])
            overall_data_len[group][machine] = len(test_data[group][machine])
    
    now = int(time.time())

    # Add the labels to Antagonist
    labels = load_labels(DATA_LABELS)
    labels = adjust_labels_timestamps(labels, now, overall_data_len, test_data)
    formatted_labels = convert_labels_to_antagonist_format(labels)
    store_data_to_db(formatted_labels)

    # Store data into influxDB
    for group in overall_data.keys():
        for machine in overall_data[group].keys():
            store_dataframe(overall_data[group][machine], group, machine, now)


if __name__ == "__main__":
    main()


# data = {
#     'grafana_annotations': [
#         {'dashboardUID': 'cd11474b-935b-4348-b6b0-622bf3adfdb3', 'panelId': 10, 'time': 1710275682664, 'timeEnd': 1710277074331, 'text': 'March 002', 'tags': ['Incident']}, 
#         {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710276601865, 'timeEnd': 1710276664293, 'text': '2 Drops of Reliability in the same sequence - 001', 'tags': ['Symptom']}, 
#         {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710275837555, 'timeEnd': 1710275840253, 'text': 'Spike of Output Load - 001', 'tags': ['Symptom']}, 
#         {'dashboardUID': 'cd11474b-935b-4348-b6b0-622bf3adfdb3', 'panelId': 10, 'time': 1710274131379, 'timeEnd': 1710275622807, 'text': 'March 001', 'tags': ['Incident']}, 
#         {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710275515473, 'timeEnd': 1710275518409, 'text': 'Little Drop of Reliability - 001', 'tags': []}, 
#         {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710274738845, 'timeEnd': 1710274743246, 'text': 'Drop of Reliability 001', 'tags': ['Symptom']}, 
#         {'dashboardUID': 'a5901a0c-71cb-42b5-a9df-cba7b7f7885b', 'panelId': 2, 'time': 1710274182040, 'timeEnd': 1710274239544, 'text': 'Strange Shape of Byte sent', 'tags': ['Symptom']}
#     ],
#     'network_anomalies': [
#         {'author': {'author_type': 'human', 'name': 'admin', 'version': 0}, 'description': 'March 001', 'id': 'c5873775-0fba-4b97-81b5-bf3fc73dcd18', 'state': 'potential', 'version': 1},
#         {'author': {'author_type': 'human', 'name': 'admin', 'version': 0}, 'description': 'March 002', 'id': '02fcd49c-f751-4f0d-b129-1b95a98ec6d4', 'state': 'potential', 'version': 1}, 
#         {'author': {'author_type': 'person', 'name': 'admin', 'version': 0}, 'description': 'March 001', 'id': 'cefaffdb-d273-4e7a-9928-7b124734e066', 'state': 'potential', 'version': 2}, 
#         {'author': {'author_type': 'person', 'name': 'admin', 'version': 0}, 'description': 'March 001', 'id': '57536c19-f458-4660-9763-6665166d903b', 'state': 'Confirmed', 'version': 3},
#         {"author": {"author_type": "person", "name": "admin", "version": 0}, "description": "March 001", "id": "57536c19-f458-4660-9763-6665166d903b", "state": "Confirmed", "version": 3}
#     ],
#     'symptoms': [
#         {'action': 'Adjacency', 'cause': 'Link-Layer', 'pattern': 'drop', 'plane': 'control', 'reason': 'Established', 'concern-score': 0.7, 'confidence-score': 1, 'description': 'Drop of Reliability 001', 'end-time': '2024-03-12T20:19:03', 'event-id': '22873b20-8e0c-4fcf-b8d9-5334b66cd43d', 'id': '0625bd54-adb4-4227-941f-b0198bd3c227', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:18:58', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710274736690&to=1710274745711&var-Resolution=1s&var-fields=reliability'}},
#         {'action': 'Reachability', 'cause': 'Peer Down', 'concern-score': 0.2, 'confidence-score': 1.0, 'description': '2 Drops of Reliability in the same sequence - 001', 'end-time': '2024-03-12T20:51:04', 'event-id': 'af152ac4-2984-44ac-946f-3c4cdd558f16', 'id': 'e1298c7d-b75a-4b7a-9f4a-f8216a8af6d3', 'pattern': 'drop', 'plane': 'control', 'reason': 'Withdraw', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:50:01', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710276535722&to=1710276752902&var-Resolution=1s&var-fields=reliability'}}, 
#         {'action': 'Adjacency', 'cause': 'Administrative', 'concern-score': 0.8, 'confidence-score': 0.4, 'description': 'Spike of Output Load - 001', 'end-time': '2024-03-12T20:37:20', 'event-id': 'd4c4d2d4-07e3-42c8-856f-e2590523e956', 'id': '2a890c1d-2e22-4b00-9cf9-6c0cc2e5a1ef', 'pattern': 'spike', 'plane': 'control', 'reason': 'Locally Teared Down', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:37:17', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710275831584&to=1710275849390&var-Resolution=1s&var-fields=output-load'}}, 
#         {'action': 'Missing', 'cause': 'Time', 'concern-score': 0.1, 'confidence-score': 0.1, 'description': 'Strange Shape of Byte sent', 'end-time': '2024-03-12T20:10:39', 'event-id': 'ce01514c-9780-4755-ae00-1c9f56223f4a', 'id': '822cedc1-aa29-4a13-92e5-0c401ef73b92', 'pattern': 'mean-shift', 'plane': 'forwarding', 'reason': 'Previous', 'source-name': 'admin', 'source-type': 'human', 'start-time': '2024-03-12T20:09:42', 'tags': {'url': 'http://localhost:3000/grafana/d/a5901a0c-71cb-42b5-a9df-cba7b7f7885b/symptom-tagging?orgId=1&from=1710274141546&to=1710274288347&var-Resolution=1s&var-fields=bytes-sent'}}
#     ],
#     'symptoms-to-network-anomalies': [
#         {"incident-id": "57536c19-f458-4660-9763-6665166d903b", "symptom-id": "e1298c7d-b75a-4b7a-9f4a-f8216a8af6d3"}, 
#         {"incident-id": "57536c19-f458-4660-9763-6665166d903b", "symptom-id": "2a890c1d-2e22-4b00-9cf9-6c0cc2e5a1ef"}
#     ]
# }
