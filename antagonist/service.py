import json
from config import env
import logging
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify, request
from database import postgresql
from domain import incident as inc, symptom as sym

logging.basicConfig(level=env.LOGGING_LEVEL)
logger = logging.getLogger(__name__)

database = postgresql.PostgresqlDatabase(
    env.POSTGRESQL_DB_HOST, env.POSTGRESQL_DB_PORT, 
    env.POSTGRESQL_DB_NAME, env.POSTGRESQL_DB_USER, 
    env.POSTGRESQL_DB_PASSWORD)
database.connect()

app = Flask(__name__)


@app.route('/api/rest/v1/symptom', methods=['POST', 'GET'])
def symptom():
    if request.method == "POST":
        symptom_data = request.get_json()
        logger.info("Received new symptom POST request")
        logger.debug(f"Symptom Data: {symptom_data}")
        try: 
            symptom_obj = sym.Symptom(symptom_data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # Store the symptom in the database
        try:
            symptom_id = database.store_symptom(symptom_obj)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify(symptom_id), 200
    if 'GET' == request.method:
        symptom_id = request.args.get('id', None)
        db_res = database.get_symptom(symptom_id)
        if not symptom_id:
            res = [dict(entry) for entry in db_res]
            return jsonify(res), 200
        return jsonify(dict(db_res)), 200


@app.route('/api/rest/v1/incident', methods=['POST', 'GET'])
def incident():
    if 'POST' == request.method:
        incident_data = request.get_json()
        logger.info("Received new incident POST request")
        logger.debug(f"Incident Data: {incident_data}")
        try: 
            incident_obj = inc.Incident(incident_data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # Store the incident in the database
        try:
            incident_id = database.store_incident(incident_obj)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify(incident_id), 200

    if 'GET' == request.method:
        incident_id = request.args.get('id', None)
        db_res = database.get_incident(incident_id)
        if not incident_id:
            res = [dict(entry) for entry in db_res]
            return jsonify(res), 200
        return jsonify(dict(db_res)), 200


# @app.route('/api/rest/v1/incident_list', methods=['GET'])
# def incident_list():
#     parse_result = urlparse(request.url)
#     dict_result = parse_qs(parse_result.query)
#     start_time = dict_result.get('start_time', [None])[0]
#     end_time = dict_result.get('end_time', [None])[0]

#     # Get all annotations from Grafana
#     annotations = grafana_annotations.get(start_time=start_time, end_time=end_time)
#     incidents = [
#         incident for incident in annotations 
#         if 'Incident' in incident.get('tags')]
#     res = list()
#     for incident in incidents:
#         try:
#             inc_description = json.loads(incident.get('text', ""))['description']
#         except json.decoder.JSONDecodeError:
#             inc_description = incident.get('text', "")
#         res.append({
#             "incident-id": incident.get('id'), 
#             "description": inc_description,
#             "from": incident.get('time'),
#             "to": incident.get('timeEnd')
#             })
#     print(res)
#     return jsonify(res), 200


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


def initialize_database():
    # TODO Make it ina  way that the password 
    ## is not stored in the configuration file
    return postgresql.PostgresqlDatabase(
        host=env.POSTGRESQL_DB_HOST, 
        port=env.POSTGRESQL_DB_PORT, 
        database=env.POSTGRESQL_DB_NAME, 
        user=env.POSTGRESQL_DB_USER, 
        password=env.POSTGRESQL_DB_PASSWORD)


if __name__ == "__main__":
    print("Starting Antagonist ... ")
    app.run(host="0.0.0.0", port=5001)
