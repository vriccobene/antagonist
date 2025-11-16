import os
from telemetry_integrations import influxdb
from data_models.label_store.api import Anomaly
from data_models.telemetry.api import DataSource


class TelemetryIntegration:

    def __init__(self, data_source: DataSource):
        self.id = data_source.id
        self.name = data_source.name
        self.description = data_source.description
        self.database_type = data_source.type.database
        self.database_version = data_source.type.version
        self.endpoint_url = data_source.end_point.url
        self.endpoint_metadata = data_source.end_point.metadata
        self.client = self._get_client()

    def _get_client(self):
        if self.database_type == "influxdb":
            self.org = os.environ.get("INFLUXDB_ORG", None)
            self.token = os.environ.get("INFLUXDB_TOKEN", None)
            # self.url = os.environ.get("INFLUXDB_URL", None)
            self.bucket = os.environ.get("INFLUXDB_BUCKET", None)
            return influxdb.InfluxDBTelemetryIntegration(
                url=self.endpoint_url,
                org=self.org,
                token=self.token,
                bucket=self.bucket
            )
        else:
            raise NotImplementedError(
                f"Database type {self.database_type} not yet supported.")

    def get_anomaly_data(self, anomaly: Anomaly, service_type: str):
        """
        Generate a query based on the symptom details and
        runs it agains the client.
        """
        if self.database_type == "influxdb":
            query = self.client.generate_query(
                service_type=service_type,
                metric=anomaly.symptom.metric,
                dimensions=anomaly.symptom.dimensions,
                start_time=anomaly.start_time,
                end_time=anomaly.end_time,
                aggregation_period="1m",
                aggregation_function="mean"
            )
        else:
            raise NotImplementedError(
                f"Database type {self.database_type} not yet supported.")

        return self.client.execute_query(query)
