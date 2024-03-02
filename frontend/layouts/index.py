from dash import html, Input, Output, State, dcc, no_update
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
            html.Div(
                children=[
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
                ], style={"margin": "1%"}
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Header",id='network-anomaly-add-new-version-modal-head')),
                    dbc.ModalBody(
                        html.Div([
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Description"), 
                                    dbc.Textarea(id='network-anomaly-add-new-version-modal-input-desc',size="lg")
                                ],
                                className="mb-3",
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Author Name"), 
                                    dbc.Input(id='network-anomaly-add-new-version-modal-input-auth')
                                ],
                                className="mb-3",
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("State"), 
                                    dbc.Select(
                                        options=[
                                            {"label": "Forecasted", "value": "Forecasted"},
                                            {"label": "Potential", "value": "Potential"},
                                            {"label": "Confirmed", "value": "Confirmed"},
                                            {"label": "Discarded", "value": "Discarded"},
                                            {"label": "Analysed", "value": "Analysed"},
                                            {"label": "Adjusted", "value": "Adjusted"},
                                        ],
                                        id='network-anomaly-add-new-version-modal-input-state'
                                    )
                                ],
                                className="mb-3",
                            ),
                        ])
                    ),
                    dbc.ModalFooter(
                        html.Div(
                            [
                                dbc.Button(
                                    "Submit", id="network-anomaly-add-new-version-modal-submit", className="ms-auto", style={"margin-right":"15px"}
                                ),
                                dbc.Button(
                                    "Undo", id="network-anomaly-add-new-version-modal-undo", className="ms-auto"
                                )
                            ]
                        )
                    ),
                ],
                id="network-anomaly-add-new-version-modal",
                size="xl",
                is_open=False,
            ),
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
    Output("network-anomaly-history-table", "rowData", allow_duplicate=True),
    Input("network-anomaly-table", "selectedRows"),
    Input('network-anomaly-visualize-button', 'n_clicks'),
    prevent_initial_call='initial_duplicate'
)
def network_anomaly_detail_visualization_button_clicked(rows, n_clicks):
    if n_clicks is None:
        return []
    row = rows[0]
    return network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=row.get("Description"))

# Callback open the modal to add a new version of a network incident
@service.app.callback(
    Output("network-anomaly-add-new-version-modal", "is_open",allow_duplicate=True),
    Output("network-anomaly-add-new-version-modal-head", "children"),
    Output("network-anomaly-add-new-version-modal-input-desc", "value"),
    Output("network-anomaly-add-new-version-modal-input-auth", "value"),
    Output("network-anomaly-add-new-version-modal-input-state", "value"),

    Input("network-anomaly-add-new-version-button", "n_clicks"),
    State("network-anomaly-history-table", "selectedRows"),
    State("network-anomaly-add-new-version-modal", "is_open"),
    prevent_initial_call='initial_duplicate'
)
def network_anomaly_detail_visualization_button_new_vesion(n_clicks, selectedRows, is_open):

    # No incidents selected
    if selectedRows is None or len(selectedRows) == 0:
        return False,"","","","FORECASTED"

    return (
        not is_open if n_clicks else is_open, 
        f"{selectedRows[0]['ID']} - Version {selectedRows[0]['Version']+1}",
        selectedRows[0]['Description'],
        selectedRows[0]['Author Name'],
        selectedRows[0]['State']
    )

# Callback close the modal to add a new version of a network incident
@service.app.callback(
    Output("network-anomaly-add-new-version-modal", "is_open",allow_duplicate=True),
    Input("network-anomaly-add-new-version-modal-undo", "n_clicks"),
    prevent_initial_call='initial_duplicate'
)
def network_anomaly_detail_visualization_new_vesion_modal_close(n_clicks):
    return False

# Callback close the modal to add a new version of a network incident
@service.app.callback(
    Output("network-anomaly-add-new-version-modal", "is_open",allow_duplicate=True),
    Output("network-anomaly-history-table", "rowData", allow_duplicate=True),
    Input("network-anomaly-add-new-version-modal-submit", "n_clicks"),
    State("network-anomaly-table", "selectedRows"),
    State("network-anomaly-history-table", "selectedRows"),
    State("network-anomaly-add-new-version-modal-input-desc", "value"),
    State("network-anomaly-add-new-version-modal-input-auth", "value"),
    State("network-anomaly-add-new-version-modal-input-state", "value"),
    prevent_initial_call='initial_duplicate'
)
def network_anomaly_detail_visualization_new_vesion_modal_close(n_clicks, rows, selectedRows,n_desc, n_auth, n_state):    
    # Initial callback
    if n_clicks is None:
        return no_update,no_update
    
    out = selectedRows[0]

    out['Version'] += 1
    out['Description']=n_desc
    out['Author Name']=n_auth
    out['State']=n_state

    success = network_anomaly_api.update_network_anomaly(out['ID'], out)

    return False, network_anomaly_detail_visualization_button_clicked(rows,1)
