import json
import uuid
import logging
import pathlib
from json.decoder import JSONDecodeError
from config import env
import grafana.auth_api as auth_api
import grafana.dashboard_api as dashboard_api
import grafana.annotation_api as annotation_api


logging.basicConfig(level=env.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


class GrafanaDashboardManager():

    def __init__(self) -> None:
        self._dashboard_cache = dict()
        self._api = auth_api.GrafanaAuthApi()
        self._dashoboard_generator = GrafanaDashboardGenerator(self._api)
        self._annotation_generator = GrafanaAnnotationGenerator(self._api)

    def add_new_dashboard_and_annotation(self, dashboard_name, tags, filters, start_time, end_time, description):
        dashboard_id = self._add_new_dashboard(dashboard_name, tags, filters)
        annotation = self._add_new_annotation(start_time, end_time, description, tags, dashboard_id)
        start_time = annotation.get('time') - 3600000
        end_time = annotation.get('timeEnd') + 3600000

        url = f"http://{env.GRAFANA_HOST_EXTERNAL}:{env.GRAFANA_PORT}/" \
               f"grafana/d/{dashboard_id}?orgId=1&from={start_time}&to={end_time}"
        return url

    def _add_new_dashboard(self, dashboard_name, tags, filters):
        """
        Create a new dashboard in Grafana, if needed, otherwise it returns the existing dashboard id
        """
        dashboard_index = self._from_tags_to_index(tags)
        dashboard_id = self._dashboard_cache.get(dashboard_index, None)
        
        if not dashboard_id:
            dashboard_id = str(uuid.uuid4())

            if 'metric' in filters:
                metric_name = filters['metric']
                filters.pop('metric')
            else: 
                metric_name = self._from_tags_to_index(tags)
            logger.info(f"Creating dashboard for metric: {metric_name}")
            annotation_tags = tags

            logger.info(f"More detailed information for the creation of the dashboard")
            logger.info(f"{dashboard_id}, {dashboard_name}, {metric_name}, {annotation_tags}, {filters}")
            self._dashoboard_generator.create_new_dashboard(
                dashboard_id, dashboard_name, metric_name, annotation_tags, filters)
        
            self._dashboard_cache[dashboard_index] = dashboard_id

        return dashboard_id

    def _add_new_annotation(self, start_time, end_time, description, tags, dashboard_id):
        return self._annotation_generator.create_new_annotation(
            start_time, end_time, description, tags, dashboard_id)

    def _from_tags_to_index(self, tags):
        res = '-'.join(tags)
        return res


class GrafanaDashboardGenerator():

    def __init__(self, grafana_auth_api) -> None:
        self._grafana_auth_api = grafana_auth_api
        self._grafana_dashboard_api = dashboard_api.GrafanaDashboardApi(self._grafana_auth_api)

    def create_new_dashboard(self, dashboard_id, dashboard_name, metric_name, annotation_tags, filters):
        dashboard_name = dashboard_name or f"Dashboard {dashboard_id}"
        path = pathlib.Path(__file__).parent.resolve()
        with open(f"{path}/Symptom Tagging-20240611.json", "r") as dashboard_file:
            f_content = dashboard_file.read()
            f_content = f_content.replace("#DASHBOARD_ID_HERE", str(dashboard_id))
            f_content = f_content.replace("#DASHBOARD_NAME_HERE", str(dashboard_name))
            f_content = f_content.replace("#METRIC_NAME_HERE", str(metric_name))
            # f_content = f_content.replace("#ANNOTATION_TAGS_HERE", str(annotation_tags))
            f_content = f_content.replace("#ANNOTATION_TAGS_HERE", str(annotation_tags).replace('"', '').replace("'", '"'))
            
            filtering_expressions = ""
            for key, value in filters.items():
                filtering_expressions += f'|> filter(fn: (r) => r[\\\"{key}\\\"] == \\\"{value}\\\")\\r\\n '
            f_content = f_content.replace("#FILTERING_EXPRESSIONS_HERE", filtering_expressions)
        try:
            dashboard_template = json.loads(f_content)
        except JSONDecodeError as e:
            print(f"Error parsing dashboard template: {e}")
        self._grafana_dashboard_api.create(dashboard_template)


class GrafanaAnnotationGenerator():

    def __init__(self, grafana_auth_api):
        self._grafana_auth_api = grafana_auth_api
        self._grafana_annotation_api = annotation_api.GrafanaAnnotationApi(self._grafana_auth_api)

    def create_new_annotation(self, start_time: int, end_time: int, description: str, tags: list, dashboard_id:str=None) -> dict:
        """
        Create a symptom annotation in Grafana format

        :param start_time: The start time of the annotation (in milliseconds)
        :type start_time: int
        :param end_time: The end time of the annotation (in milliseconds)
        :type end_time: int
        :param description: The description of the symptom
        :type description: str
        
        :return: A dictionary representing the symptom annotation in Grafana format
        :rtype: dict
        """
        dashboard_id = dashboard_id or uuid.uuid4()
        tags = tags or []
        grafana_annotation = {
            'dashboardUID': dashboard_id, 
            'panelId': 2, 
            'time': int(f'{start_time}000'), 
            'timeEnd': int(f'{end_time}000'), 
            'text': description, 
            'tags': tags + ['Symptom']
        }
        self._store_grafana_annotations(grafana_annotation)
        return grafana_annotation

    def _store_grafana_annotations(self, annotation):
        # refined_annotations = [_refine_annotation(annotation) for annotation in annotations]
        # response = grafana_annotations.post(refined_annotations)
        return self._grafana_annotation_api.post(annotation)
