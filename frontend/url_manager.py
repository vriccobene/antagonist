from dash.dependencies import Output, Input
import app as service


# @service.app.callback(
#     Output('index-page-content', 'children'),
#     Output('index-page-name', 'children'),
#     Input('url', 'pathname')
# )
# def display_page(pathname):
#     """
#     This function is a callback that is called when the URL changes
#     It returns the layout of the page that corresponds to the URL
#     """
#     if pathname == '/incidents':
#         print("Changing Page to incidents")
#         return incidents.layout, "incidents"
#     elif pathname == '/symptoms':
#         print("Changing Page to symptoms")
#         return symptoms.layout, "symptoms"
#     else:
#         print("Changing Page to incidents")
#         return incidents.layout, "incidents"


# @service.app.callback(
#     Output('callback-loaded', 'children'),
#     Input('index-page-name', 'children')
# )
# def update_callbacks():
#     print("loading callbacks")
#     from callbacks import incidents as incidents_callbacks
#     return True
