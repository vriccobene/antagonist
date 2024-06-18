import requests
import logging
from config import env
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify, request
from database import postgresql
from domain import incident as inc, symptom as sym, symptom_to_incident as sti

logging.basicConfig(level=env.LOGGING_LEVEL)
logger = logging.getLogger(__name__)

ANOMALY_METADATA_FULLY_SUPPORTED = False

database = None

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
            symptom_obj.id = symptom_id
            res = create_dashboard_for_symptom(symptom_obj)
            logger.info(f"Dashboard creation response: {res}")
            database.add_tag_to_symptom(symptom_id, "url", res)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify(symptom_id), 200
    if 'GET' == request.method:
        symptom_id = request.args.get('id', None)
        incident_id = request.args.get('incident-id', None)
        start_time = request.args.get('start-time', None)
        end_time = request.args.get('end-time', None)
        db_res = database.get_symptom(
            symptom_id=symptom_id, incident_id=incident_id, 
            start_time=start_time, end_time=end_time) 
        
        if not symptom_id:
            db_res = db_res or []
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
        db_res = database.get_incident(incident_id) or []
        if not incident_id:
            res = [dict(entry) for entry in db_res]
            return jsonify(res), 200
        return jsonify(dict(db_res)), 200


@app.route('/api/rest/v1/incident/symptom', methods=['POST', 'GET'])
def symptom_to_incident():
    """
    Link a symptom to an incident
    """
    def _convert_to_dict(val):
        {"symptom-id": val.symptom_id, "incident-id": val.get('incident-id')}
    
    if 'POST' == request.method:
        sym_to_inc_data = request.get_json()
        logger.debug("Received new symptom to incident POST request")
        logger.debug(f"Input Data: {sym_to_inc_data}")
        
        if not isinstance(sym_to_inc_data, list):
            sym_to_inc_data = [sym_to_inc_data]

        res = list()
        for obj in sym_to_inc_data:
            try:
                sym_to_inc_obj = sti.SymptomToIncident(obj)
            except ValueError as e:
                res.append({"error": str(e)})
            
            # Store the incident in the database
            try:
                res.append(database.store_symptom_incident_relation(sym_to_inc_obj))
            except Exception as e:
                res.append({"error": str(e)})
        return jsonify(res), 200

    if 'GET' == request.method:
        incident_id = request.args.get('incident-id', None)
        db_res = database.get_symptom_to_incident(incident_id)
        if not incident_id:
            return [], 200
        res = [dict(entry) for entry in db_res]
        return jsonify(res), 200


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


def _prepare_dashboard_data(symptom):
    res = dict(symptom)
    res['id'] = str(res['id'])

    res['event-id'] = str(res['event-id'])
    res['start-time'] = int(res['start-time'].timestamp())
    res['end-time'] = int(res['end-time'].timestamp())
    
    # If draft-netana-nmop-network-anomaly-semantics is supported, need to use the proper tags
    if ANOMALY_METADATA_FULLY_SUPPORTED:
        res['tags'] = {
            "plane": res['plane'],
            "action": res['action'],
            "cause": res['cause'],
            "reason": res['reason']
        }
    
    res['dashboard-name'] = " - ".join([f"{k}:{v}" for k, v in res['tags'].items()])
    return res


def create_dashboard_for_symptom(symptom):
    logger.info("Creating a new dashboard")
    try:
        respose = requests.post(
            f"http://{env.DASHBOARD_MANAGER_HOST}:{env.DASHBOARD_MANAGER_PORT}/api/rest/v1/dashboard", 
            json=_prepare_dashboard_data(symptom))
    except Exception as e:
        logger.error(f"Error while creating dashboard: {e}")
        return ""
    return respose.json()


if __name__ == "__main__":
    logger.info("Starting Antagonist ... ")

    logger.info("Loading the Database ... ")
    database = postgresql.PostgresqlDatabase(
        env.POSTGRESQL_DB_HOST, env.POSTGRESQL_DB_PORT, 
        env.POSTGRESQL_DB_NAME, env.POSTGRESQL_DB_USER, 
        env.POSTGRESQL_DB_PASSWORD)
    database.connect()

    logger.info("Ready to Accept connections ... ")
    app.run(host="0.0.0.0", port=5001)
