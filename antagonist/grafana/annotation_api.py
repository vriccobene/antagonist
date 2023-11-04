import json
import requests
from grafana import auth_api
from config import env


class GrafanaAnnotationApi:

    def __init__(self, grafana_auth:auth_api.GrafanaAuthApi=None):
        self._host = env.GRAFANA_HOST
        self._port = env.GRAFANA_PORT
        self._base_url = env.GRAFANA_BASE_URL
        self._base_api_path = f"{self._base_url}/{env.GRAFANA_ANNOTATION_PATH}"
        self._default_limit = env.GRAFANA_ANNOTATION_DEFAULT_LIMIT
        self._auth_api = grafana_auth or auth_api.GrafanaAuthApi()
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self._auth_api.get_key()}"
        }
    
    def get(self, start_time, end_time, limit=None):
        """
        Retrieves annotations from Grafana for the specified time range.

        Args:
            start_time (int): The start time of the time range in Unix timestamp format.
            end_time (int): The end time of the time range in Unix timestamp format.
            limit (int, optional): The maximum number of annotations to retrieve. 
                                    Defaults to 100 if not specified.

        Returns:
            list: A list of annotations in JSON format.
        """
        limit = limit or self._default_limit
        url = self._url_builder_get(start_time, end_time, limit)
        response = requests.get(url, headers=self._headers)
        return response.json() if response.status_code == 200 else list()
    
    def refine(self, annotation_id:str, start_time:str, end_time:str, new_annotation_descr:dict):
        # Step 1 - Retrieve any existing annotation
        existing_annotation = self._get_annotation(annotation_id, start_time, end_time)
        if not existing_annotation:
            return None
        descr = {"text": dict()}
        try:
            descr['text'] = json.loads(existing_annotation.get('text'))
            new_annotation_descr['description'] = json.loads(new_annotation_descr['description'])['description']
        except json.decoder.JSONDecodeError:
            descr['text']['description'] = existing_annotation.get('text')
        descr['text'].update(new_annotation_descr)
        descr['text'] = json.dumps(descr['text'])

        # Step 2 - Update the annotation
        url = self._url_builder_patch(annotation_id)
        print("Going to update annotation")
        print(url, self._headers, json.dumps(descr))
        response = requests.patch(
            url, headers=self._headers, data=json.dumps(descr))

        print(f"Response: {response}")
        return response.json() if response.status_code == 200 else None

    def _get_annotation(self, annotation_id, start_time, end_time):
        """
        Retrieves a single annotation by its ID.

        Args:
            annotation_id (int): The ID of the annotation to retrieve.
            start_time (int): The start time of the time range to search for annotations.
            end_time (int): The end time of the time range to search for annotations.

        Returns:
            dict or None: The annotation with the specified ID, or None if no such annotation exists.
        """
        annotations = self.get(start_time, end_time)
        if len(annotations) == 0:
            return None
        res = [sym for sym in annotations if annotation_id == sym.get('id')]
        if len(res) == 0:
            return None
        return res[0]

    def _url_builder_get(self, start, end, limit):
        """
        Builds a URL for a GET request to the Grafana annotation API.

        Args:
            start (str): The start time for the annotations query.
            end (str): The end time for the annotations query.
            limit (int): The maximum number of annotations to return.

        Returns:
            str: The URL for the GET request.
        """
        return f"{self._base_api_path}?from={start}&to={end}"\
               f"&limit={limit}"
    
    def _url_builder_patch(self, uid):
        """
        Builds the URL for a PUT request to update an annotation.

        Args:
            uid (str): The unique identifier of the annotation.

        Returns:
            str: The URL for the PUT request.
        """
        return f"{self._base_api_path}/{uid}"
