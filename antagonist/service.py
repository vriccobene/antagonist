import json
from urllib.parse import urlparse, parse_qs
from flask import Flask, jsonify, request, Response
from grafana import annotation_api, dashboard_api, auth_api
from domain import incident as inc, symptom as sym


grafana_auth = auth_api.GrafanaAuthApi()
grafana_dashboards = dashboard_api.GrafanaDashboardApi(grafana_auth)
grafana_annotations = annotation_api.GrafanaAnnotationApi(grafana_auth)


app = Flask(__name__)


@app.route('/api/rest/v1/symptom', methods=['POST'])
def symptom():
    if request.method == "POST":
        symptom_data = request.get_json()
        print(symptom_data, flush=True)
        symptom_obj = compile_symptom(symptom_data)
        new_symptom_descr = dict()
        if symptom_obj.descript:
            new_symptom_descr['description'] = symptom_obj.descript
        if symptom_obj.plane:
            new_symptom_descr['plane'] = symptom_obj.plane
        if symptom_obj.condition:
            new_symptom_descr['condition'] = symptom_obj.condition
        if symptom_obj.action:
            new_symptom_descr['action'] = symptom_obj.action
        if symptom_obj.cause:
            new_symptom_descr['cause'] = symptom_obj.cause
        if symptom_obj.pattern:
            new_symptom_descr['pattern'] = symptom_obj.pattern
        if symptom_obj.source_name:
            new_symptom_descr['source-name'] = symptom_obj.source_name
        if symptom_obj.source_type:
            new_symptom_descr['source-type'] = symptom_obj.source_type
        if symptom_obj.concern_score:
            new_symptom_descr['concern'] = symptom_obj.concern_score
        if symptom_obj.confidence_score:
            new_symptom_descr['confidence'] = symptom_obj.concern_score

        res = grafana_annotations.refine(
            annotation_id=symptom_obj.id, 
            start_time=symptom_obj.start_time,
            end_time=symptom_obj.end_time,
            new_annotation_descr=new_symptom_descr)
        return jsonify(res), 204


@app.route('/api/rest/v1/incident', methods=['POST', 'GET'])
def incident():
    if 'POST' == request.method:
        incident_data = request.get_json()
        incident_obj = compile_incident(incident_data)
        new_incident_descr = dict()
        if incident_obj.descript:
            new_incident_descr['description'] = incident_obj.descript
        if incident_obj.source_name:
            new_incident_descr['source_name'] = incident_obj.source_name
        if incident_obj.source_type:
            new_incident_descr['source_type'] = incident_obj.source_type
        
        res = grafana_annotations.refine(
            annotation_id=incident_obj.id, 
            start_time=incident_obj.start_time,
            end_time=incident_obj.end_time,
            new_annotation_descr=new_incident_descr)
        return jsonify(res), 204

    if 'GET' == request.method:
        # Get parameters from the request
        parse_result = urlparse(request.url)
        print(parse_result)

        dict_result = parse_qs(parse_result.query)
        id = dict_result.get('id', [None])[0]
        start_time = dict_result.get('start_time', [None])[0]
        end_time = dict_result.get('end_time', [None])[0]

        # Get all annotations from Grafana
        annotations = grafana_annotations.get(start_time=start_time, end_time=end_time)
        print(parse_result)

        # Find the requested incident
        requested_incident = None
        for incident in annotations:
            if str(incident.get('id')) == str(id):
                print("Incident: ", incident)
                requested_incident = incident
        if not requested_incident:
            return None, 404

        # Use the ramaining annotations to fill up the symptoms
        res = format_incident_ietf(requested_incident, annotations)

        # TODO: Finish this
        return jsonify(res), 200

    return None

@app.route('/api/rest/v1/incident_list', methods=['GET'])
def incident_list():
    parse_result = urlparse(request.url)
    dict_result = parse_qs(parse_result.query)
    start_time = dict_result.get('start_time', [None])[0]
    end_time = dict_result.get('end_time', [None])[0]

    # Get all annotations from Grafana
    annotations = grafana_annotations.get(start_time=start_time, end_time=end_time)
    incidents = [
        incident for incident in annotations 
        if 'Incident' in incident.get('tags')]
    res = list()
    for incident in incidents:
        try:
            inc_description = json.loads(incident.get('text', ""))['description']
        except json.decoder.JSONDecodeError:
            inc_description = incident.get('text', "")
        res.append({
            "incident-id": incident.get('id'), 
            "description": inc_description,
            "from": incident.get('time'),
            "to": incident.get('timeEnd')
            })
    print(res)
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


def compile_symptom(symptom_data):
    start = symptom_data.get('start-time', None)
    end = symptom_data.get('end-time', None)
    symptom_id = symptom_data.get('symptom-id', None)
    event_id = symptom_data.get('event-id', None)
    symptom_description = symptom_data.get('description', None)
    confidence_score = symptom_data.get('confidence-score', None)
    concern_score = symptom_data.get('concern-score', None)
    plane = symptom_data.get('plane', None)
    condition = symptom_data.get('condition', None) 
    action = symptom_data.get('action', None)
    cause = symptom_data.get('cause', None)
    pattern = symptom_data.get('pattern', None)
    source_type = symptom_data.get('source-type', None)
    source_name = symptom_data.get('source-name', None)
    symptom_obj = sym.Symptom(
        symptom_id, event_id, start, end, symptom_description, 
        confidence_score, concern_score, plane, condition, action, cause,  
        pattern, source_type, source_name)
    return symptom_obj


def compile_incident(incident_data):
    start = incident_data.get('start-time', None)
    end = incident_data.get('end-time', None)
    incident_id = incident_data.get('incident-id', None)
    incident_description = incident_data.get('incident-description', None)
    source_type = incident_data.get('source-type', None)
    source_name = incident_data.get('source-name', None)
    incident_obj = inc.Incident(
        incident_id, start, end, incident_description, 
        source_type, source_name)
    return incident_obj


def format_incident_ietf(requested_incident, annotations):
    annotations.remove(requested_incident)
    inc = json.loads(requested_incident.get('text'))
    inc['id'] = requested_incident.get('id')
    inc['start-time'] = requested_incident.get('time')
    inc['end-time'] = requested_incident.get('timeEnd')
    inc['description'] = requested_incident.get('description')
    inc['source'] = {"type": inc.get('source_type', 'Unknown'),
                     "name": inc.get('source_name', 'Unknown')}
    if 'source-type' in inc:
        inc.pop('source-type')
    if 'source-name' in inc:
        inc.pop('source-name')
    inc['symptoms'] = list()
    
    # TODO: Need to update the model ("concern_score" instead of just "concern")
    for symptom in annotations:
        sym = dict()
        if isinstance(symptom.get('text'), dict):
            sym = json.loads(symptom.get('text'))
        else:
            sym = dict()
            sym['description'] = symptom.get('description')
        sym['id'] = symptom.get('id')
        sym['event-id'] = symptom.get('event-id')
        sym['confidence-score'] = symptom.get('confidence')
        sym['concern-score'] = symptom.get('concern')
        sym['tags'] = list()
        sym['tags'] = list()
        sym['tags'].append({"plane": sym.get('plane', None)})
        sym['tags'].append({"action": sym.get('action', None)})
        sym['tags'].append({"reason": sym.get('reason', None)})
        sym['tags'].append({"cause": sym.get('cause', None)})
        sym['start-time'] = symptom.get('time')
        sym['end-time'] = symptom.get('timeEnd')
        sym['source'] = {"type": sym.get('source_type', None),
                         "name": sym.get('source_name', None)}
        if 'source-type' in sym:
            sym.pop('source-type')
        if 'source-name' in sym:
            sym.pop('source-name')
        sym['pattern'] = symptom.get('pattern')
        inc['symptoms'].append(sym)
        
    return inc


if __name__ == "__main__":
    print("Starting Antagonist ... ")
    app.run(host="0.0.0.0", port=5001)
