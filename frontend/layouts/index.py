from dash import html, Input, Output, State, dcc, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from integration import symptom_api, network_anomaly_api
import app as service


layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-name",
                 children=["index"], style={"display": "none"}),
        html.Div(id="page-content", children=[
            html.Div(
                children=[
                    dbc.Row([
                        dbc.Col(html.H1("Network Anomalies"), xxl=4)
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
                            ), xxl=9
                        ),
                        dbc.Col(
                            dbc.Row(
                                [
                                    dbc.Button(
                                        "Visualize Details", id='network-anomaly-visualize-button', style={'visibility': "hidden"}),
                                    html.Div(style={"margin": "5px"}),
                                    dbc.Button(
                                        "Compare Versions", id='network-anomaly-compare-button', style={'visibility': "hidden"})
                                ]
                            ),
                            xxl=1
                        )
                    ]),
                ],
                style={"margin": "1%"}
            ),
            html.Div(
                children=dbc.Tabs([
                    dbc.Tab([
                        html.Div(
                            [
                                dbc.Row([
                                    dbc.Col(
                                        html.H1("Network anomaly stages"), xxl=4)
                                ]),
                                dbc.Row([
                                    dbc.Col(
                                        dag.AgGrid(
                                            id="network-anomaly-history-table",
                                            className="ag-theme-alpine selection",
                                            columnDefs=network_anomaly_api.get_network_anomaly_col_def(
                                                False),
                                            rowData=[],
                                            columnSize="sizeToFit",
                                            style={"height": 300,
                                                   "width": "100%"},
                                            dashGridOptions={
                                                'rowSelection': 'single',
                                                'suppressRowClickSelection': True,
                                                'enableCellTextSelection': True,
                                                'ensureDomOrder': True,
                                                "suppressCellFocus": True, "animateRows": False
                                            }
                                        ),
                                        xxl=9
                                    ),
                                    dbc.Col([
                                        dbc.Button(
                                            "Add New Version", id='network-anomaly-add-new-version-button', style={"width": "100%", "visibility": "hidden"}
                                        ),
                                        html.Div(style={"margin": "15px"}),
                                        dbc.Button(
                                            "Inspect", id='network-anomaly-inspect-button', style={"width": "100%"}
                                        ),
                                    ], xxl=1),
                                ]),

                                html.Div(style={"margin": "15px"}),
                                dbc.Row([
                                    dbc.Col(
                                        html.H1("Network anomaly symptoms"), xxl=6)
                                ]),
                                dbc.Row([
                                    dbc.Col(
                                        [
                                            dag.AgGrid(
                                                id="symptom-table",
                                                className="ag-theme-alpine selection",
                                                columnDefs=symptom_api.get_symptoms_col_def(),
                                                rowData=[],
                                                columnSize="sizeToFit",
                                                style={"height": 300,
                                                       "width": "100%"},
                                                dashGridOptions={
                                                    'rowSelection': 'single',
                                                    'suppressRowClickSelection': True,
                                                    'enableCellTextSelection': True,
                                                    'ensureDomOrder': True,
                                                    "suppressCellFocus": True, "animateRows": False
                                                }
                                            )
                                        ],
                                        xxl=9
                                    )
                                ])
                            ],
                            style={"margin": "1%"}
                        )
                    ],
                        label="Network anomaly details",
                        tab_id="network-anomaly-tabs-details"),
                    dbc.Tab(
                        html.Div([
                            dbc.Row([
                                dbc.Col(
                                    html.H1("", id='network-anomaly-add-new-version-modal-head'), xxl=8)
                            ]),
                            html.Div(style={"margin": "15px"}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("Author Name"),
                                            dbc.Input(
                                                id='network-anomaly-add-new-version-modal-input-auth')
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("State"),
                                            dbc.Select(
                                                options=[
                                                    {"label": "Forecasted",
                                                        "value": "Forecasted"},
                                                    {"label": "Potential",
                                                        "value": "Potential"},
                                                    {"label": "Confirmed",
                                                        "value": "Confirmed"},
                                                    {"label": "Discarded",
                                                        "value": "Discarded"},
                                                    {"label": "Analysed",
                                                        "value": "Analysed"},
                                                    {"label": "Adjusted",
                                                        "value": "Adjusted"},
                                                ],
                                                id='network-anomaly-add-new-version-modal-input-state'
                                            )
                                        ],
                                        className="mb-3",
                                    ),
                                ], xxl=4)
                            ]),
                        ], style={"margin": "1%"}),
                        label="Network anomaly symptoms",
                        tab_id="network-anomaly-tabs-new-version"
                    ),
                    dbc.Tab(
                        html.Div([
                            dbc.Row([
                                dbc.Col(
                                    dbc.Row([
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupText(
                                                    "Version 1"),
                                                dbc.Select(
                                                    options=[
                                                        {"label": "Forecasted",
                                                            "value": "Forecasted"},
                                                    ],
                                                    id='network-anomaly-compare-input-v1'
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            "Author: Antonio Roberto", id='network-anomaly-compare-author-v1'
                                        ),
                                        html.Div(
                                            "State: Forecasted", id='network-anomaly-compare-state-v1'
                                        ),
                                        html.Div(style={"margin": "15px"}),
                                        dag.AgGrid(
                                            id="compare-symptom-table-v1",
                                            className="ag-theme-alpine selection",
                                            columnDefs=symptom_api.get_symptoms_col_def(),
                                            rowData=[],
                                            columnSize="sizeToFit",
                                            style={"height": 300,
                                                   "width": "100%"},
                                            dashGridOptions={
                                                'rowSelection': 'single',
                                                'suppressRowClickSelection': True,
                                                'enableCellTextSelection': True,
                                                'ensureDomOrder': True,
                                                "suppressCellFocus": True, "animateRows": False
                                            }
                                        )
                                    ]), xxl=5
                                ),
                                dbc.Col(xxl=1),
                                dbc.Col(
                                    dbc.Row([
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupText(
                                                    "Version 2"),
                                                dbc.Select(
                                                    options=[
                                                        {"label": "Forecasted",
                                                            "value": "Forecasted"},
                                                    ],
                                                    id='network-anomaly-compare-input-v2'
                                                )
                                            ],
                                            className="mb-3",
                                        ),
                                        html.Div(
                                            "Author: Antonio Roberto", id='network-anomaly-compare-author-v2'
                                        ),
                                        html.Div(
                                            "State: Forecasted", id='network-anomaly-compare-state-v2'
                                        ),
                                        html.Div(style={"margin": "15px"}),
                                        dag.AgGrid(
                                            id="compare-symptom-table-v2",
                                            className="ag-theme-alpine selection",
                                            columnDefs=symptom_api.get_symptoms_col_def(),
                                            rowData=[],
                                            columnSize="sizeToFit",
                                            style={"height": 300,
                                                   "width": "100%"},
                                            dashGridOptions={
                                                'rowSelection': 'single',
                                                'suppressRowClickSelection': True,
                                                'enableCellTextSelection': True,
                                                'ensureDomOrder': True,
                                                "suppressCellFocus": True, "animateRows": False
                                            }
                                        )
                                    ]), xxl=5
                                ),
                            ]),
                        ], style={"margin": "1%"}),
                        label="Network anomaly versions comparison",
                        tab_id="network-anomaly-tabs-compare-versions"
                    ),
                ], id="network-anomaly-tabs"),
                style={"margin": "1%"}
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader("Error"),
                    dbc.ModalBody(
                        html.Div("Select at least one incident")
                    ),
                ],
                id="network-anomaly-selection-error-modal",
                size="lg",
                is_open=False,
            ),
        ]),
    ]
)

# TODO: Add capability of adding a new version
# TODO: Add capability of comparing 2 versions


# Buttons visualization callbacks

@service.app.callback(
    Output("network-anomaly-visualize-button", "style"),
    Output("network-anomaly-compare-button", "style"),
    Output("network-anomaly-add-new-version-button", "style"),
    Input("network-anomaly-table", "selectedRows"),
)
def network_anomaly_detail_visualization_button_show(rows):
    if rows is None or len(rows) == 0:
        return {"visibility": "hidden"}, {"visibility": "hidden"}, {"visibility": "hidden"}

    return {"visibility": "initial"}, {"visibility": "initial"}, {"visibility": "initial"}


@service.app.callback(
    Output("network-anomaly-inspect-button", "style"),
    Input("network-anomaly-history-table", "selectedRows"),
)
def network_anomaly_symptom_visualization_button_show(rows):
    if rows is None or len(rows) == 0:
        return {"visibility": "hidden", "width": "100%"}

    return {"visibility": "initial", "width": "100%"}


# Buttons click callbacks

@service.app.callback(
    Output("symptom-table", "rowData"),
    State("network-anomaly-history-table", "selectedRows"),
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
    State("network-anomaly-table", "selectedRows"),
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
    Output("network-anomaly-add-new-version-modal",
           "is_open", allow_duplicate=True),
    Output("network-anomaly-add-new-version-modal-head", "children"),
    Output("network-anomaly-add-new-version-modal-input-auth", "value"),
    Output("network-anomaly-add-new-version-modal-input-state", "value"),
    Output("network-anomaly-tabs", "active_tab"),

    Input("network-anomaly-add-new-version-button", "n_clicks"),
    State("network-anomaly-history-table", "rowData"),
    State("network-anomaly-add-new-version-modal", "is_open"),
    prevent_initial_call='initial_duplicate'
)
def network_anomaly_detail_visualization_button_new_vesion(n_clicks, rows, is_open):

    # No incidents selected
    rows.sort(key=lambda x: x['Version'])
    if rows is None or len(rows) == 0:
        return False, "", "", "FORECASTED", no_update

    return (
        False,
        f"{rows[-1]['ID']} - Version {rows[-1]['Version']+1}",
        rows[-1]['Author Name'],
        rows[-1]['State'],
        "network-anomaly-tabs-new-version"
    )

# Callback close the modal to add a new version of a network incident


@service.app.callback(
    Output("network-anomaly-add-new-version-modal",
           "is_open", allow_duplicate=True),
    Output("network-anomaly-history-table", "rowData", allow_duplicate=True),
    Input("network-anomaly-add-new-version-modal-submit", "n_clicks"),
    State("network-anomaly-table", "selectedRows"),
    State("network-anomaly-history-table", "rowData"),
    State("network-anomaly-add-new-version-modal-input-auth", "value"),
    State("network-anomaly-add-new-version-modal-input-state", "value"),
    prevent_initial_call='initial_duplicate'
)
def network_anomaly_detail_visualization_new_vesion_modal_close(n_clicks, rows, selectedRows, n_auth, n_state):
    # Initial callback
    if n_clicks is None:
        return no_update, no_update

    # No incidents selected
    selectedRows.sort(key=lambda x: x['Version'])

    out = selectedRows[-1]

    out['Version'] += 1
    out['Author Name'] = n_auth
    out['State'] = n_state

    success = network_anomaly_api.update_network_anomaly(out['ID'], out)

    return False, network_anomaly_detail_visualization_button_clicked(rows, 1)

# Compare versions section callbacks


@service.app.callback(
    Output("network-anomaly-compare-input-v1", "options"),
    Output("network-anomaly-compare-input-v2", "options"),
    Input("network-anomaly-table", "selectedRows"),
)
def network_anomaly_compare_versions_available(rows):
    if rows is None or len(rows) == 0:
        return [], []

    row = rows[0]
    annotation_history = network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=row.get("Description"))

    avail_vers = [{"label": f"Version {k['Version']}",
                   "value": k['Version']} for k in annotation_history]

    return avail_vers, avail_vers


@service.app.callback(
    Output("network-anomaly-compare-author-v1", "children"),
    Output("network-anomaly-compare-state-v1", "children"),
    Output("compare-symptom-table-v1", "rowData"),
    Input("network-anomaly-table", "selectedRows"),
    Input("network-anomaly-compare-input-v1", "value"),
)
def network_anomaly_compare_versions_available(rows, selection):
    if rows is None or len(rows) == 0 or selection is None:
        return "Author:", "State:", []

    row = rows[0]

    annotation_history = network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=row.get("Description"))

    print("Selection:", selection)
    print("History:", annotation_history)
    curr_version = [
        k for k in annotation_history if k['Version'] == int(selection)][0]

    # TODO: Get symptom IDs from the Incident
    symptom_ids = ["2fc901ba-c941-4dba-a3a6-94ca3618a24d"]
    symptoms = symptom_api.get_symptoms(subset=False, symptom_ids=symptom_ids)

    return f"Author: {curr_version['Author Name']}", f"State: {curr_version['State']}", symptoms


@service.app.callback(
    Output("network-anomaly-compare-author-v2", "children"),
    Output("network-anomaly-compare-state-v2", "children"),
    Output("compare-symptom-table-v2", "rowData"),
    Input("network-anomaly-table", "selectedRows"),
    Input("network-anomaly-compare-input-v2", "value"),
)
def network_anomaly_compare_versions_available(rows, selection):
    if rows is None or len(rows) == 0 or selection is None:
        return "Author:", "State:", []

    row = rows[0]

    annotation_history = network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=row.get("Description"))

    print("Selection:", selection)
    print("History:", annotation_history)
    curr_version = [
        k for k in annotation_history if k['Version'] == int(selection)][0]

    # TODO: Get symptom IDs from the Incident
    symptom_ids = ["2fc901ba-c941-4dba-a3a6-94ca3618a24d"]
    symptoms = symptom_api.get_symptoms(subset=False, symptom_ids=symptom_ids)

    return f"Author: {curr_version['Author Name']}", f"State: {curr_version['State']}", symptoms
