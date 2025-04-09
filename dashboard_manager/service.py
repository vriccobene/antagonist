import time
import uuid
from config import env
import logging
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify, request
from grafana import dashboard_api as api


logging.basicConfig(level=env.LOGGING_LEVEL)
logger = logging.getLogger(__name__)

app = Flask(__name__)


import grafana.dashboard_manager as dm
dashboard_manager = dm.GrafanaDashboardManager()


@app.route('/api/rest/v1/dashboard', methods=['POST'])
def dashboard():
    logger.info("Creating a new dashboard")

    # Prepare input data
    input_params = request.get_json()

    logger.info("Received data for dashboard creation")
    logger.info(input_params)

    dashboard_name = input_params.get('dashboard-name', None)
    filters = input_params.get('tags', {})
    tags = [f"{k}:{v}" for k, v in filters.items()]
    
    # TODO Manage the annoator name and type in the antagonist service
    filters = {k: v for k, v in filters.items() if k not in ['annotator-name', 'annotator-type']}

    logger.info("Prepared data for dashboard creation")
    logger.info(f"{dashboard_name}, {tags} , {filters}")

    start_time = input_params.get('start-time', None)
    end_time = input_params.get('end-time', None)
    description = input_params.get('description', None)

    logger.info("Prepared data for annotation creation")
    logger.info(f"{start_time}, {end_time}, {description}")

    res = dashboard_manager.add_new_dashboard_and_annotation(
        dashboard_name, tags, filters, start_time, end_time, description)

    return jsonify(res), 200


@app.after_request
def allow_foreign_origin(response):
    """
    Allow other origin (grant)
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers['X-Content-Type-Options'] = "*"
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Request-Method'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST, PUT, PATCH'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


if __name__ == "__main__":
    logger.info("Starting Dashboard Manager ... ")
    logger.info("Ready to Accept connections ... ")
    app.run(host="0.0.0.0", port=5002)
