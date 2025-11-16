from .base import DataSourceAdapter
from typing import Dict, Any
from influxdb_client import InfluxDBClient


class InfluxDBAdapter(DataSourceAdapter):

    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket

    def test_connection(self) -> bool:
        try:
            health = self.client.health()
            return health.status == "pass"
        except Exception:
            return False

    def query_metric(
            self,
            metric_mapping: Dict[str, Any],
            entity_fields: Dict[str, Any]
    ) -> dict:

        field = metric_mapping["field"]
        host = entity_fields.get("host")
        flux_query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: -1h)
              |> filter(fn: (r) => r._measurement == "{field}")
              {f'|> filter(fn: (r) => r.host == "{host}")' if host else ''}
              |> mean()
        '''
        query_api = self.client.query_api()
        result = query_api.query(org=self.org, query=flux_query)
        return {"result": [
            record.values for table in result
            for record in table.records]}
