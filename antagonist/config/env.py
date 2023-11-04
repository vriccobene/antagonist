# TODO: Get this stuff from the environment variables of the container

GRAFANA_HOST = "grafana"
GRAFANA_PORT = "3000"
GRAFANA_BASE_URL = f"http://{GRAFANA_HOST}:{GRAFANA_PORT}/api"

# Grafana Annotation API
GRAFANA_ANNOTATION_PATH = "annotations"
GRAFANA_ANNOTATION_DEFAULT_LIMIT = 100

# Grafana auth api
GRAFANA_AUTH_PATH = "auth/keys"
GRAFANA_USER = "admin"
GRAFANA_PASSWD = "password"

# Grafana dashboard api
GRAFANA_DASHBOARD_PATH = "dashboards"

# PostgreSQL
POSTGRESQL_DB_NAME = 'incidents'
POSTGRESQL_DB_USER = 'grafana'
POSTGRESQL_DB_PASSWORD = 'grafana-password'
# POSTGRESQL_DB_HOST = 'postgres'
# POSTGRESQL_DB_PORT = '5432'
POSTGRESQL_DB_HOST = 'localhost'
POSTGRESQL_DB_PORT = '5433'
