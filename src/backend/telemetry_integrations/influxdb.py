"""

It is necessary to enable the generation of queries like the following,
in this file.

from(bucket: "anomaly_detection")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "machine")
  |> filter(fn: (r) => r["_field"] == "active_opens")
  |> filter(fn: (r) => r["machine-name"] == "machine-1-6")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")


-----------------------------


from(bucket: "network_telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "interface")
  |> filter(fn: (r) => r["_field"] == "active_opens")
  |> filter(fn: (r) => r["vpn-id"] == "machine-1-6")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")

from(bucket: "network_telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "bmp")
  |> filter(fn: (r) => r["_field"] == "XXX")
  |> filter(fn: (r) => r["machine-name"] == "machine-1-6")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")

from(bucket: "network_telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "ipfix")
  |> filter(fn: (r) => r["_field"] == "octectDeltaCount")
  |> filter(fn: (r) => r["machine-name"] == "machine-1-6")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")

"""

import datetime
from typing import Dict, Optional
from influxdb_client import InfluxDBClient


class InfluxDBTelemetryIntegration:

    def __init__(self, url, org, token, bucket):
        self.url = url
        self.org = org
        self.token = token
        self.bucket = bucket
        self.client = InfluxDBClient(
            url=self.url,
            org=self.org,
            token=self.token
        )
        self.query_api = self.client.query_api()

    def generate_query(
        self,
        service_type: str,
        metric: str,
        dimensions: Dict[str, str | int | float],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        aggregation_period: Optional[str] = "1m",
        aggregation_function: Optional[str] = "mean"
    ) -> str:
        """
        Generate an InfluxDB query based on the provided parameters.
        Expects start_time and end_time to be timezone-aware datetimes in UTC.
        """
        # Ensure datetimes are timezone-aware (assume UTC if naive)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=datetime.timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=datetime.timezone.utc)

        # Convert to UTC-based epoch seconds
        start = int(start_time.timestamp())
        end = int(end_time.timestamp())
        # Add 100% Padding
        interval_size = end - start
        start = start - interval_size
        end = end + interval_size

        query = 'from(bucket: "network_telemetry")  '
        query += f'  |> range(start: {start}, '
        query += f'stop: {end})  '
        query += f'  |> filter(fn: (r) => r["_measurement"] == '\
                 f'"{service_type}")  '
        query += f'  |> filter(fn: (r) => r["_field"] == "{metric}")  '

        for key, value in dimensions.items():
            query += f'  |> filter(fn: (r) => r["{key}"] == "{value}")  '
        if aggregation_period and aggregation_function:
            query += f'  |> aggregateWindow(every: {aggregation_period},   '
            query += f'  fn: {aggregation_function}, createEmpty: false)  '
            query += f'  |> yield(name: "{aggregation_function}")  '
        return query

    def execute_query(self, query: str):
        """
        Execute the generated InfluxDB query and return the results.
        """
        result = self.query_api.query(org=self.org, query=query)
        data = {}
        for table in result:
            for record in table.records:
                timestamp = int(record.get_time().timestamp())
                value = record.get_value()
                data[str(timestamp)] = value
        return data
