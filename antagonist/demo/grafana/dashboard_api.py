import requests
from grafana import auth_api
from config import env


class GrafanaDashboardApi:

    def __init__(self, grafana_auth:auth_api.GrafanaAuthApi=None):
        self._host = env.GRAFANA_HOST
        self._port = env.GRAFANA_PORT
        self._base_url = env.GRAFANA_BASE_URL
        self._base_api_path = f"{self._base_url}/{env.GRAFANA_DASHBOARD_PATH}"
        self._auth_api = grafana_auth or auth_api.GrafanaAuthApi()
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self._auth_api.get_key()}"
        }
    
    def     get(self, uid=None):
        url = self._url_builder(uid)
        response = requests.get(url, headers=self._headers)
        return response.json() if response.status_code == 200 else None
    
    def _url_builder(self, uid=None):
        no_id_url = f"{self._base_api_path}"
        if uid:
            return f"{no_id_url}/uid/{uid}"
