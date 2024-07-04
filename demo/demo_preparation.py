import uuid
import time
import math
import pathlib
import datetime
import requests
import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


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
                    "columns": label["columns"]
                })

    return res


def send_data_to_antagonist(data_to_store):
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

    # Load the network anomaly annotations to Antagonist
    labels = load_labels(DATA_LABELS)
    labels = adjust_labels_timestamps(labels, now, overall_data_len, test_data)
    formatted_labels = convert_labels_to_antagonist_format(labels)
    send_data_to_antagonist(formatted_labels)

    # Store data into influxDB
    for group in overall_data.keys():
        for machine in overall_data[group].keys():
            store_dataframe(overall_data[group][machine], group, machine, now)


if __name__ == "__main__":
    main()
