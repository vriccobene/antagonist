# TODO: Get this stuff from the environment variables of the container

import logging
LOGGING_LEVEL = logging.DEBUG

# GRAFANA_HOST = "grafana"
# GRAFANA_PORT = "3000"
# GRAFANA_BASE_URL = f"http://{GRAFANA_HOST}:{GRAFANA_PORT}/api"

# # Grafana Annotation API
# GRAFANA_ANNOTATION_PATH = "annotations"
# GRAFANA_ANNOTATION_DEFAULT_LIMIT = 100

# # Grafana auth api
# GRAFANA_AUTH_PATH = "auth/keys"
# GRAFANA_USER = "admin"
# GRAFANA_PASSWD = "password"

# # Grafana dashboard api
# GRAFANA_DASHBOARD_PATH = "dashboards"

# PostgreSQL
POSTGRESQL_DB_NAME = 'network_anomalies'
POSTGRESQL_DB_USER = 'antagonist'
POSTGRESQL_DB_PASSWORD = 'antagonist-password'
# POSTGRESQL_DB_HOST = 'localhost'#'postgres'
# POSTGRESQL_DB_PORT = '5433'#'5432'
POSTGRESQL_DB_HOST = 'postgres-db'
POSTGRESQL_DB_PORT = '5432'

DASHBOARD_MANAGER_HOST = 'dashboard-manager'
DASHBOARD_MANAGER_PORT = '5002'
