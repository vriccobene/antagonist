"""
This class provides functionality for reading the Server Machine Dataset (SMD) from the `data` folder.

The `SMD` class has the following methods:

- `get_metric_names()`: Returns a list of the available metric names in the dataset.
- `read_dataset(group_name=None, metric_name=None, train=True)`: Reads the dataset for the specified group and metric. If no group or metric is specified, it reads the dataset for all groups and all metrics.

The dataset is organized into three groups, with each group containing multiple machine files. The class provides the file structure information in the `data_structure` attribute.
"""

import os
import datetime
import pandas as pd
import influxdb_client

from typing import List, Union


# InfluxDB configuration
INFLUX_ORG = "ietf"
INFLUX_PORT = "8086"
INFLUX_HOST = "localhost"
INFLUX_BUCKET = "anomaly_detection"
INFLUX_TOKEN = "qT83QJVt1wENkP3s8Lfgyw0A5mGMQ5NFDApl5xOYKC3B_7tM5eVm8G0cnUsCzEG_8J3YEk0o2i6oH6L9masMxA=="

data_structure = {
    "Group 1": [
        "machine-1-1.txt",
        "machine-1-2.txt",
        "machine-1-3.txt",
        "machine-1-4.txt",
        "machine-1-5.txt",
        "machine-1-6.txt",
        "machine-1-7.txt",
        "machine-1-8.txt",
    ],
    "Group 2": [
        "machine-2-1.txt",
        "machine-2-2.txt",
        "machine-2-3.txt",
        "machine-2-4.txt",
        "machine-2-5.txt",
        "machine-2-6.txt",
        "machine-2-7.txt",
        "machine-2-8.txt",
        "machine-2-9.txt",
    ],
    "Group 3": [
        "machine-3-1.txt",
        "machine-3-2.txt",
        "machine-3-3.txt",
        "machine-3-4.txt",
        "machine-3-5.txt",
        "machine-3-6.txt",
        "machine-3-7.txt",
        "machine-3-8.txt",
        "machine-3-9.txt",
        "machine-3-10.txt",
        "machine-3-11.txt",
    ],
}


class SMD:
    """
    A class for reading and processing the Server Machine Dataset.

    Attributes:
        dataset_folder (str): The path to the folder containing the dataset.
        train_folder (str): The path to the folder containing the training data.
        test_folder (str): The path to the folder containing the test data.
        test_labels_folder (str): The path to the folder containing the test labels.
        interpretation_labels_folder (str): The path to the folder containing the interpretation labels.
        data_structure (dict): A dictionary containing the file names for each group in the dataset.
    """

    def __init__(self, dataset_folder="./data/ServerMachineDataset"):
        self.dataset_folder = dataset_folder
        self.train_folder = os.path.join(self.dataset_folder, "train")
        self.test_folder = os.path.join(self.dataset_folder, "test")
        self.test_labels_folder = os.path.join(self.dataset_folder, "test_label")
        self.interpretation_labels_folder = os.path.join(
            self.dataset_folder, "interpretation_label"
        )

        self.data_structure = data_structure

    def get_metric_names(self):
        """
        Returns a list of metric names in the dataset.

        Returns:
            list: A list of metric names.
        """
        return [
            "cpu_r",
            "load_1",
            "load_5",
            "load_15",
            "mem_shmem",
            "mem_u",
            "mem_u_e",
            "total_mem",
            "disk_q",
            "disk_r",
            "disk_rb",
            "disk_svc",
            "disk_u",
            "disk_w",
            "disk_wa",
            "disk_wb",
            "si",
            "so",
            "eth1_fi",
            "eth1_fo",
            "eth1_pi",
            "eth1_po",
            "tcp_tw",
            "tcp_use",
            "active_opens",
            "curr_estab",
            "in_errs",
            "in_segs",
            "listen_overflows",
            "out_rsts",
            "out_segs",
            "passive_opens",
            "retransegs",
            "tcp_timeouts",
            "udp_in_dg",
            "udp_out_dg",
            "udp_rcv_buf_errs",
            "udp_snd_buf_errs",
        ]

    def read_dataset(
        self,
        group_name: Union[List[str], str] = None,
        metric_name: Union[List[str], str] = None,
        train: bool = True,
        retrieve_labels: bool = False,
    ) -> List[pd.DataFrame]:
        """
        Reads the dataset for a given group and metric. If the group and metric are not specified,
        reads the dataset for all groups and all metrics.

        Args:
            group_name (Union[List[str], str], optional): The name(s) of the group(s) to read. If not provided, all groups are read.
            metric_name (Union[List[str], str], optional): The name(s) of the metric(s) to read. If not provided, all metrics are read.
            train (bool, optional): Whether to read the training or test data. Defaults to True (training data).
            retrieve_labels (bool, optional): Whether to retrieve labels for the test data. Defaults to False.

        Returns:
            List[pd.DataFrame]: A list of DataFrames containing the requested data.
        """
        data = {}
        files_to_read = []
        if group_name is not None:
            files_to_read = self.data_structure[group_name]
        else:
            files_to_read = [
                file for group in self.data_structure.values() for file in group
            ]

        for file in files_to_read:
            data[file] = pd.read_csv(
                os.path.join(self.train_folder if train else self.test_folder, file),
                header=None,
                names=self.get_metric_names(),
                usecols=[metric_name] if metric_name else None,
            )

        if not train and retrieve_labels:
            # load table for each file and concatenate to the dataframe read before
            for file in files_to_read:
                data[file] = pd.concat(
                    [
                        data[file],
                        pd.read_csv(
                            os.path.join(self.test_labels_folder, file),
                            header=None,
                            names=["label"],
                            usecols=[0],
                            index_col=False,
                        ),
                    ],
                    axis=1,
                )

        # Adding timestamp column
        for file, df in data.items():
            df["timestamp"] = pd.date_range(
                start=datetime.datetime(2020, 1, 1, 0, 0, 0),
                freq="min",
                periods=df.shape[0],
                name="timestamp",
            )

        return list(data.values()), list(data.keys())

    def get_interpretation_labels(self, filename):
        """
        Reads the interpretation labels for a given machine file. The interpretation labels
        represents the index of the metrics that are anomalous in each period of time.

        Args:
            filename (str): The name of the machine file.

        Returns:
            pd.DataFrame: A DataFrame containing the interpretation labels.
        """
        inter_labels = pd.read_csv(
            os.path.join(self.interpretation_labels_folder, filename),
            header=None,
            names=["period", "metrics"],
            index_col=False,
            sep=":",
        )

        # split intervals
        inter_labels[["start", "end"]] = (
            inter_labels["period"].str.split("-", expand=True).astype(int)
        )

        # Add timestamps
        timestamps = (
            pd.date_range(
                start=datetime.datetime(2020, 1, 1, 0, 0, 0),
                freq="min",
                periods=inter_labels["end"].max() + 1,
                name="timestamp",
            )
            .to_frame()
            .reset_index(drop=True)
        )

        inter_labels["start"] = (
            timestamps["timestamp"].iloc[inter_labels["start"]].values
        )
        inter_labels["end"] = timestamps["timestamp"].iloc[inter_labels["end"]].values

        # Convert metrics to array
        inter_labels["metrics"] = (
            inter_labels["metrics"].str.split(",").apply(lambda x: [int(i) for i in x])
        )

        return inter_labels[["start", "end", "metrics"]]


class SMDInfluxDB:

    def __init__(
        self,
        influx_host: str = INFLUX_HOST,
        influx_port: str = INFLUX_PORT,
        influx_org: str = INFLUX_ORG,
        influx_bucket: str = INFLUX_BUCKET,
        influx_token: str = INFLUX_TOKEN,
    ) -> None:
        self.influx_host = influx_host
        self.influx_port = influx_port
        self.influx_org = influx_org
        self.influx_bucket = influx_bucket
        self.influx_token = influx_token
        self.data_structure = data_structure

    def get_metric_names(self):
        """
        Returns a list of metric names in the dataset.

        Returns:
            list: A list of metric names.
        """
        return [
            "cpu_r",
            "load_1",
            "load_5",
            "load_15",
            "mem_shmem",
            "mem_u",
            "mem_u_e",
            "total_mem",
            "disk_q",
            "disk_r",
            "disk_rb",
            "disk_svc",
            "disk_u",
            "disk_w",
            "disk_wa",
            "disk_wb",
            "si",
            "so",
            "eth1_fi",
            "eth1_fo",
            "eth1_pi",
            "eth1_po",
            "tcp_tw",
            "tcp_use",
            "active_opens",
            "curr_estab",
            "in_errs",
            "in_segs",
            "listen_overflows",
            "out_rsts",
            "out_segs",
            "passive_opens",
            "retransegs",
            "tcp_timeouts",
            "udp_in_dg",
            "udp_out_dg",
            "udp_rcv_buf_errs",
            "udp_snd_buf_errs",
        ]

    def read_dataset(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        metric_name: Union[List[str], str] = None,
        machine_name: Union[List[str], str] = None
    ) -> List[pd.DataFrame]:

        client = influxdb_client.InfluxDBClient(
            url=f"http://{INFLUX_HOST}:{INFLUX_PORT}", token=INFLUX_TOKEN
        )
        query_api = client.query_api()

        if metric_name:
            metric_name = (
                metric_name if isinstance(metric_name, list) else [metric_name]
            )
        if machine_name:
            machine_name = (
                machine_name if isinstance(machine_name, list) else [machine_name]
            )
        query = (
            f'from(bucket: "anomaly_detection") |> range(start: {start_date.isoformat()}Z, stop: {end_date.isoformat()}Z)'
            + (
                (
                    " |> filter(fn:(r) => "
                    + " or ".join(
                        [(f'r._field == "' + str(k) + '"') for k in metric_name]
                    )
                    + ")"
                )
                if metric_name
                else ""
            )
            + (
                (
                    " |> filter(fn:(r) => "
                    + " or ".join(
                        [(f'r.machine == "' + str(k) + '"') for k in machine_name]
                    )
                    + ")"
                )
                if machine_name
                else ""
            )
        )

        #print(query)
        result = query_api.query(org=self.influx_org, query=query)

        results = []
        for table in result:
            for record in table.records:
                results.append(record.values)

        df = pd.DataFrame.from_records(results)
        retrieve = []
        files = []
        for group, machine in (
            df[["group", "machine"]].drop_duplicates().values.tolist()
        ):
            df_tmp = df[(df["group"] == group) & (df["machine"] == machine)]
            retrieve.append(
                df_tmp[["_time", "_value", "_field"]]
                .pivot(columns="_field", values="_value", index="_time")
                .reset_index(names='timestamp')
            )
            files.append(machine + ".txt")

        return retrieve, files


if __name__ == "__main__":
    db = SMDInfluxDB()
    db.read_dataset(
        start_date=datetime.datetime(2024, 6, 13, 0, 0, 0),
        end_date=datetime.datetime(2024, 6, 14, 12, 0, 0),
        machine_name="machine-1-1",
    )

    