import copy
import requests
import logging
from domain import network_anomaly as na, symptom_to_network_anomaly as stna
from config import env
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify, request
from database import postgresql
from domain import symptom as sym

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
            logger.exception(f"Error while creating symptom: {e}")
            return jsonify({"error": str(e)}), 400
        
        # Store the symptom in the database
        try:
            symptom_id = database.store_symptom(symptom_obj)
            symptom_obj.id = symptom_id
            res = create_dashboard_for_symptom(symptom_obj)
            logger.info(f"Dashboard creation response: {res}")
            database.add_tag_to_symptom(symptom_id, "url", res)
        except Exception as e:
            logger.exception(f"Error while storing symptom: {e}")
            return jsonify({"error": str(e)}), 500
        return jsonify(symptom_id), 200
    if 'GET' == request.method:
        symptom_id = request.args.get('id', None)
        network_anomaly_id = request.args.get('network-anomaly-id', None)
        start_time = request.args.get('start-time', None)
        end_time = request.args.get('end-time', None)
        min_confidence_score = request.args.get('min-confidence-score', 0.0)
        min_concern_score = request.args.get('min-concern-score', 0.0)
        annotator_name = request.args.get('annotator-name', None)
        annotator_type = request.args.get('annotator-type', None)
        tags = request.get_json().get('tags', None)

        db_res = database.get_symptom(
            symptom_id=symptom_id, network_anomaly_id=network_anomaly_id, 
            start_time=start_time, end_time=end_time, min_confidence_score=min_confidence_score,
            min_concern_score=min_concern_score, annotator_name=annotator_name, 
            annotator_type=annotator_type, tags=tags) 
        
        if not symptom_id:
            db_res = db_res or []
            res = [dict(entry) for entry in db_res]
            return jsonify(res), 200
            
        return jsonify(dict(db_res)), 200


@app.route('/api/rest/v1/network_anomaly', methods=['POST', 'GET'])
def network_anomaly():
    if 'POST' == request.method:
        network_anomaly_data = request.get_json()
        logger.info("Received new network anomaly POST request")
        logger.debug(f"Network anomaly Data: {network_anomaly_data}")
        try: 
            network_anomaly_obj = na.NetworkAnomaly(network_anomaly_data)
        except ValueError as e:
            logger.exception(f"Error while creating network anomaly: {e}")
            return jsonify({"error": str(e)}), 400
        
        # Store the network anomaly in the database
        try:
            network_anomaly_id = database.store_network_anomaly(network_anomaly_obj)
        except Exception as e:
            logger.exception(f"Error while storing network anomaly: {e}")
            return jsonify({"error": str(e)}), 500
        return jsonify(network_anomaly_id), 200

    if 'GET' == request.method:
        network_anomaly_id = request.args.get('id', None)
        db_res = database.get_network_anomaly(network_anomaly_id) or []
        if not network_anomaly_id:
            res = [dict(entry) for entry in db_res]
            return jsonify(res), 200
        return jsonify(dict(db_res)), 200


@app.route('/api/rest/v1/network_anomaly/symptom', methods=['POST', 'GET'])
def symptom_to_network_anomaly():
    """
    Link a symptom to an network anomaly
    """
    def _convert_to_dict(val):
        {"symptom-id": val.symptom_id, "network-anomaly-id": val.get('network-anomaly-id')}
    
    if 'POST' == request.method:
        sym_to_inc_data = request.get_json()
        logger.debug("Received new symptom to network anomaly POST request")
        logger.debug(f"Input Data: {sym_to_inc_data}")
        
        if not isinstance(sym_to_inc_data, list):
            sym_to_inc_data = [sym_to_inc_data]

        res = list()
        for obj in sym_to_inc_data:
            try:
                sym_to_inc_obj = stna.SymptomToNetworkAnomaly(obj)
            except ValueError as e:
                logger.exception(f"Error while creating symptom to network anomaly: {e}")
                res.append({"error": str(e)})
            
            # Store the network anomaly in the database
            try:
                res.append(database.store_symptom_network_anomaly_relation(sym_to_inc_obj))
            except Exception as e:
                logger.exception(f"Error while storing symptom to network anomaly: {e}")
                res.append({"error": str(e)})
        return jsonify(res), 200

    if 'GET' == request.method:
        network_anomaly_id = request.args.get('network-anomaly-id', None)
        db_res = database.get_symptom_to_network_anomaly(network_anomaly_id)
        if not network_anomaly_id:
            return [], 200
        res = [dict(entry) for entry in db_res]
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
    res.pop('annotator')
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
        symptom_local = copy.deepcopy(symptom)
        symptom_local.tags['annotator-name'] = symptom_local.annotator.name
        symptom_local.tags['annotator-type'] = symptom_local.annotator.annotator_type
    except Exception as e:
        logger.error(f"Error while preparing dashboard data: {e}")
        logger.exception(f"{e}")
    try:
        respose = requests.post(
            f"http://{env.DASHBOARD_MANAGER_HOST}:{env.DASHBOARD_MANAGER_PORT}/api/rest/v1/dashboard", 
            json=_prepare_dashboard_data(symptom_local))
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
