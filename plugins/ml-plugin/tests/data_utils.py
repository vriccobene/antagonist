"""
This class provides functionality for reading the Server Machine Dataset (SMD) from the `data` folder.

The `SMD` class has the following methods:

- `get_metric_names()`: Returns a list of the available metric names in the dataset.
- `read_dataset(group_name=None, metric_name=None, train=True)`: Reads the dataset for the specified group and metric. If no group or metric is specified, it reads the dataset for all groups and all metrics.

The dataset is organized into three groups, with each group containing multiple machine files. The class provides the file structure information in the `data_structure` attribute.
"""

"""This file contains the python code for reading the Server Machine Dataset (SMD) in the `data` folder.
"""

"""
The `SMD` class provides a convenient interface for reading the Server Machine Dataset (SMD) used for machine learning tasks.

The class initializes with a dataset folder path, and provides methods to read the dataset for a given group and/or metric. If no group or metric is specified, the dataset for all groups and all metrics is read.

The `get_metric_names()` method returns a list of all the available metric names in the dataset.

The `read_dataset()` method reads the dataset for the specified group and/or metric, and returns a pandas DataFrame containing the data.
"""
import os
import pandas as pd

from typing import Optional, List, Union


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

        self.data_structure = {
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
    ) -> pd.DataFrame:
        """
        Reads the dataset for a given group and metric. If the group and metric are not specified,
        reads the dataset for all groups and all metrics.

        Args:
            group_name (Union[List[str], str], optional): The name(s) of the group(s) to read. If not provided, all groups are read.
            metric_name (Union[List[str], str], optional): The name(s) of the metric(s) to read. If not provided, all metrics are read.
            train (bool, optional): Whether to read the training or test data. Defaults to True (training data).

        Returns:
            pd.DataFrame: A DataFrame containing the requested data.
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
                columns=self.get_metric_names(),
                usecols=[metric_name] if metric_name else None,
            )

        return pd.concat(data.values(), axis=1, keys=data.keys())
