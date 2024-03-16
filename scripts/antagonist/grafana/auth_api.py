import json
import requests
from config import env


class GrafanaAuthApi:

    def __init__(self):
        self._key_name = 'antagonist'
        self._user = env.GRAFANA_USER
        self._passwd = env.GRAFANA_PASSWD
        self._auth = (self._user, self._passwd)
        self._host = env.GRAFANA_HOST
        self._port = env.GRAFANA_PORT
        self._base_url = env.GRAFANA_BASE_URL
        self._base_api_path = f"{self._base_url}/{env.GRAFANA_AUTH_PATH}"
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self._key = self._initialize_key()

    def get_key(self):
        return self._key
    
    def _initialize_key(self):
        """
        Initialize the authentication key for the Grafana API
        """
        # Check if among the available keys there is one that collides 
        # with the one I want to create
        keys = [k for k in self._get() if k.get('name') == self._key_name]
        key = keys[0] if keys else None
        # If there is , I delete it
        del_resp = self._delete(key.get('id')) if key else None
        # And then I create a new one and return it
        return self._create().get('key', None)
    
    def _get(self):
        """
        Retrieves all the authentication keys currently registered on Grafana
        """
        response = requests.get(
            self._base_api_path, headers=self._headers, auth=self._auth)
        return response.json()

    def _create(self):
        """
        Use basic authentication for this request
        """
        data = {"name": self._key_name, "role": 'Admin'}
        response = requests.post(
            self._base_api_path, headers=self._headers, data=json.dumps(data), 
            auth=self._auth)
        return response.json() if response.status_code == 200 else {}

    def _delete(self, key_id):
        """
        Retrieves all the authentication keys currently registered on Grafana
        """
        response = requests.delete(
            f"{self._base_api_path}/{key_id}", headers=self._headers, auth=self._auth)
        return response.json()

    def _url_builder(self):
        return f"http://{self._user}:{self._passwd}@"\
               f"{self._host}:{self._port}/{self._base_api_path}"
