# TODO: Get this stuff from the environment variables of the container

import logging
LOGGING_LEVEL = logging.DEBUG

GRAFANA_HOST = "grafana"
GRAFANA_HOST_EXTERNAL = "localhost"
GRAFANA_PORT = "3000"
GRAFANA_BASE_URL = f"http://{GRAFANA_HOST}:{GRAFANA_PORT}/api"

# Grafana auth api
GRAFANA_AUTH_PATH = "auth/keys"
GRAFANA_USER = "admin"
GRAFANA_PASSWD = "password"

# Grafana dashboard api
GRAFANA_DASHBOARD_PATH = "dashboards"

# Grafana Annotation API
GRAFANA_ANNOTATION_PATH = "annotations"
GRAFANA_ANNOTATION_DEFAULT_LIMIT = 100
