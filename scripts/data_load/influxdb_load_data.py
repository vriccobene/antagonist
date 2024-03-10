import time
import math
import pandas
import pathlib
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


TIME_COL = 'time'
IGNORE_COLUMNS = ['name', 'EncodingPath']
REMOVE_DUPLICATES = True
INFLUX_HOST = 'localhost'
INFLUX_PORT = '8086'
INFLUX_BUCKET = 'anomaly_detection'
INFLUX_ORG = 'ietf'
INFLUX_TOKEN = 'qT83QJVt1wENkP3s8Lfgyw0A5mGMQ5NFDApl5xOYKC3B_7tM5eVm8G0cnUsCzEG_8J3YEk0o2i6oH6L9masMxA=='
MEASUREMENT = "BGP"
data_file = pathlib.Path(__file__).parent.parent.parent / 'data' / 'bgpclear.csv'


def main():
    # Load data in a dataframe and clean it
    df = pandas.read_csv(data_file.absolute())
    df.drop_duplicates(inplace=True)
    df.set_index(TIME_COL, inplace=True)
    df.drop(columns=IGNORE_COLUMNS, inplace=True)

    # Connect to InfluxDB
    client = InfluxDBClient(url=f'http://{INFLUX_HOST}:{INFLUX_PORT}', token=INFLUX_TOKEN)
    influx_api = client.write_api(write_opton=SYNCHRONOUS)

    # Prepare and store data points
    # timebase = 171008  # Fixed timestamp on 10th March 2024
    timebase = str(time.time())[0:6] # Current timestamp
    step = 1000
    start, end = 0, step
    while True:
        points = []
        for index, row in df[start: end].iterrows():
            # Adjust timestamp to fall within the retention period
            timestamp = f"{timebase}{str(index)[6:]}"

            for col in row.index:
                # Do not store categorical metrics
                if isinstance(row[col], str):
                    continue
                # Skip nan values
                if row[col] == 'NaN' or math.isnan(row[col]):
                    continue
                field = f'{col}="{row[col]}"' if isinstance(row[col], str) else f'{col}={row[col]}'
                points.append(f"{MEASUREMENT},test=1 {field} {timestamp}")

        res = influx_api.write(INFLUX_BUCKET, INFLUX_ORG, points)
        print(res)
        start, end = end, end + step
        print(f"DF [{start}: {end}] - points: {len(points)}")
        points = list()


if __name__ == "__main__":
    main()
