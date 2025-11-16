import random
import uuid
import time
import math
import pathlib
import datetime
import requests
import pandas as pd
from data_models.label_store import api
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


ANTAGONIST_URL = "http://localhost:8000"

# InfluxDB configuration
INFLUX_ORG = 'ietf'
INFLUX_PORT = '8086'
INFLUX_HOST = 'localhost'
INFLUX_BUCKET = 'network_telemetry'
INFLUX_TOKEN = 'qT83QJVt1wENkP3s8Lfgyw0A5mGMQ5NFDApl5xOYKC3B_7tM5eVm8G0cnUsCzEG_8J3YEk0o2i6oH6L9masMxA=='


DEMO_DATA_DIRECTORY = pathlib.Path(".") \
        / "OmniAnomaly" / "ServerMachineDataset"
DATA_TEST_SET = DEMO_DATA_DIRECTORY / "test"
DATA_TRAINING_SET = DEMO_DATA_DIRECTORY / "train"
DATA_LABELS = DEMO_DATA_DIRECTORY / "interpretation_label"


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
        res[group][machine] = pd.read_csv(
            data_file, sep=",", header=None, names=metric_names())

    return res


def format_time(epoch_time: int) -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch_time))


def define_symptom(
        group, machine, start_time, end_time, event_id, metric, description):
    return {
        'start-time': format_time(start_time),
        'end-time': format_time(end_time),
        'event-id': event_id,
        'concern-score': 0.9,
        'confidence-score': 1,
        'description': description,
        'pattern': '',
        'annotator': {
            'name': 'ground-truth',
            'annotator_type': 'human'
        },
        'tags': {
            'machine': machine,
            'group': group,
            'metric': metric
        }
    }


class Machine(api.Service):
    name: str

    def __init__(self, **data):
        super().__init__(**data)


machines = {}


def get_machine(name: str) -> api.Service:
    global machines
    machine = machines.get(name, None)
    print("Machine:", machine)
    if machine:
        res = {
            "id": machine["id"],
            "type": "machine",
            "name": machine["name"]
        }
    else:
        res = {
            "id": uuid.uuid4(),
            "type": "machine",
            "name": name
        }
        machines[name] = res
    print(res)
    return res


def define_relevant_state(group, machine, label):
    start_time = datetime.datetime.fromtimestamp(
        label['rows'][0], tz=datetime.timezone.utc)
    end_time = datetime.datetime.fromtimestamp(
        label['rows'][1], tz=datetime.timezone.utc)
    anomalies = list()
    for metric in label['columns']:
        description = f'Symptom on {metric} of {machine}'
        anomalies.append(api.Anomaly(
            description=description,
            start_time=start_time,
            end_time=end_time,
            state=api.State.confirmed,
            confidence_score=round(random.uniform(0.6, 1), 2),
            annotator=api.Annotator(
                name="OmniAnomaly-ground-truth",
                annotator_type=api.AnnotatorType.human),
            symptom=api.Symptom(
                concern_score=round(random.uniform(0.6, 1), 2),
                metric=metric,
                dimensions={"machine-name": machine, "group-name": group})
        ))
    description = f'Network anomaly on {machine} at ' \
                  f'{format_time(start_time.timestamp())}'
    return api.RelevantState(
        description=description,
        start_time=start_time,
        end_time=end_time,
        state=api.State.potential,
        confidence_score=round(random.uniform(0.6, 1), 2),
        concern_score=round(random.uniform(0.6, 1), 2),
        service=get_machine(machine),
        anomaly=anomalies,
        publisher=api.Publisher(
            name="OmniAnomaly-ground-truth", version="1.0")
    )


def generate_anomalies(data):
    relevant_states = list()
    for group, machine_labels in data.items():
        for machine in machine_labels:
            for label in machine_labels[machine]:
                relevant_states.append(
                    define_relevant_state(group, machine, label))
    return relevant_states


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
                # points.append(f"{measurement},omnids=1,{fields_str} {field} {index}000000000")
                points.append(f"machine,omnids=1,{fields_str} {field} {index}000000000")

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
        fields={"group-name": group, "machine-name": machine})


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
                    "rows": [now - ((test_data_len - int(row)) * 60)
                             for row in label["rows"]],
                    "columns": label["columns"]
                })

    return res


def send_anomalies_to_antagonist(anomalies):
    # Store the data in Antagonist
    for relevant_state in anomalies:
        # Convert pydantic model to dict before serializing
        response = requests.post(
            f"{ANTAGONIST_URL}/api/v1/label-store/relevant-state/",
            json=relevant_state.model_dump(mode="json"))
        response.raise_for_status()


import json

def create_data_source():
    url = f"{ANTAGONIST_URL}/api/v1/telemetry/data-source/"

    payload = json.dumps({
        "name": "InfluxDB",
        "description": "Telemetry DB",
        "type": {
            "database": "influxdb",
            "version": "1.12"
        },
        "end_point": {
            "url": f"http://influxdb:{INFLUX_PORT}/",
            "metadata": {
                "bucket": INFLUX_BUCKET,
                "org": INFLUX_ORG
            }
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print("Create Data Source Response:", response.text)
    return response.json()


def create_monitored_entity_type(data_source_id):
    import requests
    import json

    url = "http://localhost:8000/api/v1/telemetry/monitored-entity-type/"

    payload = json.dumps({
        "name": "machine",
        "description": "Machine in the Datacenter",
        "data_source_id": data_source_id
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def main():
    print("Loading training data...")
    training_data = load_data(DATA_TRAINING_SET)
    print("Loading test data...")
    test_data = load_data(DATA_TEST_SET)
    print("Loading labels...")
    labels = load_labels(DATA_LABELS)
    print("Data loading completed")

    # Add the data source to Antagonist
    data_source_id = create_data_source()
    create_monitored_entity_type(data_source_id)


    # Merge training and test data
    print("Merging training and test data...")
    overall_data = dict()
    overall_data_len = dict()
    for group in training_data.keys():
        overall_data[group] = overall_data.get(group, dict())
        overall_data_len[group] = overall_data_len.get(group, dict())
        for machine in training_data[group].keys():
            overall_data[group][machine] = pd.concat([
                training_data[group][machine], test_data[group][machine]])
            overall_data_len[group][machine] = len(test_data[group][machine])
    print("Merging completed")

    now = int(time.time())

    # Load the network anomaly annotations to Antagonist
    print("Sending anomaly labels to Antagonist...")
    labels = adjust_labels_timestamps(labels, now, overall_data_len, test_data)
    anomalies = generate_anomalies(labels)
    send_anomalies_to_antagonist(anomalies)
    print("Done.")

    # Store data into influxDB
    print("Storing data into InfluxDB...")
    for group in overall_data.keys():
        for machine in overall_data[group].keys():
            store_dataframe(overall_data[group][machine], group, machine, now)
    print("Done.")


if __name__ == "__main__":
    main()
