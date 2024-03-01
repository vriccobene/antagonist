from dash import html, Input, Output, dcc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from integration import symptom_api, network_anomaly_api
import app as service


layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-name", children=["index"], style={"display": "none"}),
        html.Div(id="page-content", children=[
            html.Div(children=[
                dbc.Row([
                    dbc.Col(html.H1("Network Anomalies"), width=3),
                    dbc.Col(html.H1("Network Anomaly Stages"), width=9)
                ]),
                dbc.Row([
                    dbc.Col(
                        dag.AgGrid(
                            id="network-anomaly-table",
                            className="ag-theme-alpine selection",
                            columnDefs=network_anomaly_api.get_network_anomaly_col_def(),
                            rowData=network_anomaly_api.get_network_anomalies(),
                            columnSize="sizeToFit",
                            style={"height": 300, "width": "100%"},
                            dashGridOptions={
                                'rowSelection': 'single', 
                                'suppressRowClickSelection': True, 
                                'enableCellTextSelection': True, 
                                'ensureDomOrder': True,
                                "suppressCellFocus": True, "animateRows": False
                            }
                        ), width=2
                    ),
                    dbc.Col(dbc.Button("Visualize Details", id='network-anomaly-visualize-button'), width=1),
                    dbc.Col(
                        dag.AgGrid(
                            id="network-anomaly-history-table",
                            className="ag-theme-alpine selection",
                            columnDefs=network_anomaly_api.get_network_anomaly_col_def(False),
                            rowData=[],
                            columnSize="sizeToFit",
                            style={"height": 300, "width": "100%"},
                            dashGridOptions={
                                'rowSelection': 'single', 
                                'suppressRowClickSelection': True, 
                                'enableCellTextSelection': True, 
                                'ensureDomOrder': True,
                                "suppressCellFocus": True, "animateRows": False
                            }
                        ), width=9)
                ])
            ], style={"margin": "1%"}),
            html.Div(),
            html.Div(children=[
                dbc.Row(
                    [
                        dbc.Col(html.H1("Network Anomaly Stages"), width=6),
                        dbc.Col(html.H1("Symptoms"), width=6),
                    ]),
                    
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Inspect", id='network-anomaly-inspect-button', style={"width": "100%"}),
                        dbc.Button("Add New Version", id='network-anomaly-add-new-version-button', style={"width": "100%"})
                    ], width=1),
                    dbc.Col([
                        dag.AgGrid(
                            id="symptom-table",
                            className="ag-theme-alpine selection",
                            columnDefs=symptom_api.get_symptoms_col_def(),
                            rowData=[],
                            columnSize="sizeToFit",
                            style={"height": 300, "width": "100%"},
                            dashGridOptions={
                                'rowSelection': 'single', 
                                'suppressRowClickSelection': True, 
                                'enableCellTextSelection': True, 
                                'ensureDomOrder': True,
                                "suppressCellFocus": True, "animateRows": False
                            }
                        )
                    ], width=6)
                ])
            ], style={"margin": "1%"})
        ]),
    ]
)

# TODO: Add capability of adding a new version
# TODO: Add capability of comparing 2 versions


@service.app.callback(
    Output("symptom-table", "rowData"),
    Input("network-anomaly-history-table", "selectedRows"),
    Input('network-anomaly-inspect-button', 'n_clicks')
)
def network_anomaly_detail_visualization_button_clicked(rows, n_clicks):
    if n_clicks is None:
        return []
    row = rows[0]
    # TODO: Get symptom IDs from the Incident
    symptom_ids = ["2fc901ba-c941-4dba-a3a6-94ca3618a24d"]
    return symptom_api.get_symptoms(subset=False, symptom_ids=symptom_ids)


@service.app.callback(
    Output("network-anomaly-history-table", "rowData"),
    Input("network-anomaly-table", "selectedRows"),
    Input('network-anomaly-visualize-button', 'n_clicks')
)
def network_anomaly_detail_visualization_button_clicked(rows, n_clicks):
    if n_clicks is None:
        return []
    row = rows[0]
    return network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=row.get("Description"))
