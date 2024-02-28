import json
from dash import Input, Output
import app as service


# @service.app.callback(
#     Output("symptoms-incident-selected", "children"),
#     Input("symptom-incident-data", "loading_state"),
#     Input('index-page-name', 'children'),
#     Input("global-incident", "children")
# )
# def symptoms_reload_page(loading_state, page_name, global_incident):
#     print(loading_state)
#     print(page_name)
#     if page_name != "symptoms":
#         raise Exception("Nothing to do")
    
#     # incident = json.loads(global_incident)
#     print(global_incident)


# def update_global_state(incident_id, incident_description, incident_author, incident_version, incident_state):
#     global_incident_id = incident_id
#     global_incident_description = incident_description
#     global_incident_author = incident_author
#     global_incident_version = incident_version
#     global_incident_state = incident_state
