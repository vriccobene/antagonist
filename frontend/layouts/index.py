from dash import html, Input, Output, State, dcc, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from integration import symptom_api, network_anomaly_api
import app as service
from datetime import date


layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-name", children=["index"], style={"display": "none"}),
        html.Div(
            id="page-content",
            children=[
                html.Div(
                    children=[
                        dbc.Row([dbc.Col(html.H1("Network Anomalies"), xxl=4)]),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dag.AgGrid(
                                        id="network-anomaly-table",
                                        className="ag-theme-alpine selection",
                                        columnDefs=network_anomaly_api.get_network_anomaly_col_def(),
                                        rowData=network_anomaly_api.get_network_anomalies(),
                                        columnSize="sizeToFit",
                                        style={"height": 300, "width": "100%"},
                                        dashGridOptions={
                                            "rowSelection": "single",
                                            "suppressRowClickSelection": True,
                                            "enableCellTextSelection": True,
                                            "ensureDomOrder": True,
                                            "suppressCellFocus": True,
                                            "animateRows": False,
                                        },
                                    ),
                                    xxl=9,
                                ),
                                dbc.Col(
                                    dbc.Row(
                                        [
                                            dbc.Button(
                                                "Visualize Details",
                                                id="network-anomaly-visualize-button",
                                                style={"visibility": "hidden"},
                                            ),
                                            html.Div(style={"margin": "5px"}),
                                            dbc.Button(
                                                "Compare Versions",
                                                id="network-anomaly-compare-button",
                                                style={"visibility": "hidden"},
                                            ),
                                        ]
                                    ),
                                    xxl=1,
                                ),
                            ]
                        ),
                    ],
                    style={"margin": "1%"},
                ),
                html.Div(
                    children=dbc.Tabs(
                        [
                            dbc.Tab(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.H3(
                                                            "Network anomaly stages"
                                                        ),
                                                        xxl=4,
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dag.AgGrid(
                                                            id="network-anomaly-history-table",
                                                            className="ag-theme-alpine selection",
                                                            columnDefs=network_anomaly_api.get_network_anomaly_col_def(
                                                                False
                                                            ),
                                                            rowData=[],
                                                            columnSize="sizeToFit",
                                                            style={
                                                                "height": 300,
                                                                "width": "100%",
                                                            },
                                                            dashGridOptions={
                                                                "rowSelection": "single",
                                                                "suppressRowClickSelection": True,
                                                                "enableCellTextSelection": True,
                                                                "ensureDomOrder": True,
                                                                "suppressCellFocus": True,
                                                                "animateRows": False,
                                                            },
                                                        ),
                                                        xxl=9,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Button(
                                                                "Add New Version",
                                                                id="network-anomaly-add-new-version-button",
                                                                style={
                                                                    "width": "100%",
                                                                    "visibility": "hidden",
                                                                },
                                                            ),
                                                            html.Div(
                                                                style={"margin": "15px"}
                                                            ),
                                                            dbc.Button(
                                                                "Inspect",
                                                                id="network-anomaly-inspect-button",
                                                                style={"width": "100%"},
                                                            ),
                                                        ],
                                                        xxl=1,
                                                    ),
                                                ]
                                            ),
                                            html.Div(style={"margin": "15px"}),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.H3(
                                                            "Network anomaly symptoms"
                                                        ),
                                                        xxl=6,
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dag.AgGrid(
                                                                id="symptom-table",
                                                                className="ag-theme-alpine selection",
                                                                columnDefs=symptom_api.get_symptoms_col_def(),
                                                                rowData=[],
                                                                columnSize="sizeToFit",
                                                                style={
                                                                    "height": 300,
                                                                    "width": "100%",
                                                                },
                                                                dashGridOptions={
                                                                    "rowSelection": "single",
                                                                    "suppressRowClickSelection": True,
                                                                    "enableCellTextSelection": True,
                                                                    "ensureDomOrder": True,
                                                                    "suppressCellFocus": True,
                                                                    "animateRows": False,
                                                                },
                                                            )
                                                        ],
                                                        xxl=9,
                                                    )
                                                ]
                                            ),
                                        ],
                                        style={"margin": "1%"},
                                    )
                                ],
                                label="Network anomaly details",
                                tab_id="network-anomaly-tabs-details",
                            ),
                            dbc.Tab(
                                html.Div(
                                    [
                                        html.Div(style={"margin": "15px"}),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [html.H3("New version")], xxl=5
                                                ),
                                                dbc.Col([], xxl=1),
                                                dbc.Col(
                                                    [html.H3("Add symptoms")], xxl=5
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText(
                                                                    "Author Name"
                                                                ),
                                                                dbc.Input(
                                                                    id="network-anomaly-add-new-version-input-auth"
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText(
                                                                    "State"
                                                                ),
                                                                dbc.Select(
                                                                    options=[
                                                                        {
                                                                            "label": "Forecasted",
                                                                            "value": "Forecasted",
                                                                        },
                                                                        {
                                                                            "label": "Potential",
                                                                            "value": "Potential",
                                                                        },
                                                                        {
                                                                            "label": "Confirmed",
                                                                            "value": "Confirmed",
                                                                        },
                                                                        {
                                                                            "label": "Discarded",
                                                                            "value": "Discarded",
                                                                        },
                                                                        {
                                                                            "label": "Analysed",
                                                                            "value": "Analysed",
                                                                        },
                                                                        {
                                                                            "label": "Adjusted",
                                                                            "value": "Adjusted",
                                                                        },
                                                                    ],
                                                                    id="network-anomaly-add-new-version-input-state",
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                    ],
                                                    xxl=3,
                                                ),
                                                dbc.Col([], xxl=3),
                                                dbc.Col(
                                                    [
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText(
                                                                    "Start"
                                                                ),
                                                                dbc.Input(
                                                                    id="date-input-start",
                                                                    type="date",
                                                                    placeholder="Select a date",
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText(
                                                                    "Start time"
                                                                ),
                                                                dbc.Input(
                                                                    type="time",
                                                                    id="time-input-start",
                                                                    placeholder="Select a date",
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                    ],
                                                    xxl=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText(
                                                                    "End"
                                                                ),
                                                                dbc.Input(
                                                                    id="date-input-end",
                                                                    type="date",
                                                                    placeholder="Select a date",
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText(
                                                                    "End time"
                                                                ),
                                                                dbc.Input(
                                                                    type="time",
                                                                    id="time-input-end",
                                                                    placeholder="Select a date",
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                    ],
                                                    xxl=2,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Search",
                                                            id="network-anomaly-add-new-version-search-sympt",
                                                            style={
                                                                "visibility": "initial"
                                                            },
                                                        ),
                                                    ],
                                                    xxl=1,
                                                ),
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dag.AgGrid(
                                                            id="new-version-symptom-table-current",
                                                            className="ag-theme-alpine selection",
                                                            columnDefs=symptom_api.get_symptoms_col_def(),
                                                            rowData=[],
                                                            columnSize="sizeToFit",
                                                            style={
                                                                "height": 300,
                                                                "width": "100%",
                                                            },
                                                            dashGridOptions={
                                                                "rowSelection": "multiple",
                                                                "suppressRowClickSelection": True,
                                                                "enableCellTextSelection": True,
                                                                "ensureDomOrder": True,
                                                                "suppressCellFocus": True,
                                                                "animateRows": False,
                                                            },
                                                        )
                                                    ],
                                                    xxl=5,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Add symptom",
                                                            id="network-anomaly-add-new-version-add-sympt",
                                                            style={
                                                                "visibility": "initial"
                                                            },
                                                        ),
                                                        html.Div(
                                                            style={"margin": "15px"}
                                                        ),
                                                        dbc.Button(
                                                            "Delete symptom",
                                                            id="network-anomaly-add-new-version-del-sympt",
                                                            style={
                                                                "visibility": "initial"
                                                            },
                                                        ),
                                                        html.Div(
                                                            style={"margin": "15px"}
                                                        ),
                                                        dbc.Button(
                                                            "Submit version",
                                                            id="network-anomaly-add-new-version-submit",
                                                            style={
                                                                "visibility": "initial"
                                                            },
                                                        ),
                                                    ],
                                                    xxl=1,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dag.AgGrid(
                                                            id="new-version-symptom-table-search",
                                                            className="ag-theme-alpine selection",
                                                            columnDefs=symptom_api.get_symptoms_col_def(),
                                                            rowData=[],
                                                            columnSize="sizeToFit",
                                                            style={
                                                                "height": 300,
                                                                "width": "100%",
                                                            },
                                                            dashGridOptions={
                                                                "rowSelection": "multiple",
                                                                "suppressRowClickSelection": True,
                                                                "enableCellTextSelection": True,
                                                                "ensureDomOrder": True,
                                                                "suppressCellFocus": True,
                                                                "animateRows": False,
                                                            },
                                                        )
                                                    ],
                                                    xxl=5,
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={"margin": "1%"},
                                ),
                                label="Network anomaly symptoms",
                                tab_id="network-anomaly-tabs-new-version",
                            ),
                            dbc.Tab(
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Row(
                                                        [
                                                            dbc.InputGroup(
                                                                [
                                                                    dbc.InputGroupText(
                                                                        "Version 1"
                                                                    ),
                                                                    dbc.Select(
                                                                        options=[
                                                                            {
                                                                                "label": "Forecasted",
                                                                                "value": "Forecasted",
                                                                            },
                                                                        ],
                                                                        id="network-anomaly-compare-input-v1",
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),
                                                            html.Div(
                                                                "Author: Antonio Roberto",
                                                                id="network-anomaly-compare-author-v1",
                                                            ),
                                                            html.Div(
                                                                "State: Forecasted",
                                                                id="network-anomaly-compare-state-v1",
                                                            ),
                                                            html.Div(
                                                                style={"margin": "15px"}
                                                            ),
                                                            dag.AgGrid(
                                                                id="compare-symptom-table-v1",
                                                                className="ag-theme-alpine selection",
                                                                columnDefs=symptom_api.get_symptoms_col_def(),
                                                                rowData=[],
                                                                columnSize="sizeToFit",
                                                                style={
                                                                    "height": 300,
                                                                    "width": "100%",
                                                                },
                                                                dashGridOptions={
                                                                    "rowSelection": "single",
                                                                    "suppressRowClickSelection": True,
                                                                    "enableCellTextSelection": True,
                                                                    "ensureDomOrder": True,
                                                                    "suppressCellFocus": True,
                                                                    "animateRows": False,
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                    xxl=5,
                                                ),
                                                dbc.Col(xxl=1),
                                                dbc.Col(
                                                    dbc.Row(
                                                        [
                                                            dbc.InputGroup(
                                                                [
                                                                    dbc.InputGroupText(
                                                                        "Version 2"
                                                                    ),
                                                                    dbc.Select(
                                                                        options=[
                                                                            {
                                                                                "label": "Forecasted",
                                                                                "value": "Forecasted",
                                                                            },
                                                                        ],
                                                                        id="network-anomaly-compare-input-v2",
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),
                                                            html.Div(
                                                                "Author: Antonio Roberto",
                                                                id="network-anomaly-compare-author-v2",
                                                            ),
                                                            html.Div(
                                                                "State: Forecasted",
                                                                id="network-anomaly-compare-state-v2",
                                                            ),
                                                            html.Div(
                                                                style={"margin": "15px"}
                                                            ),
                                                            dag.AgGrid(
                                                                id="compare-symptom-table-v2",
                                                                className="ag-theme-alpine selection",
                                                                columnDefs=symptom_api.get_symptoms_col_def(),
                                                                rowData=[],
                                                                columnSize="sizeToFit",
                                                                style={
                                                                    "height": 300,
                                                                    "width": "100%",
                                                                },
                                                                dashGridOptions={
                                                                    "rowSelection": "single",
                                                                    "suppressRowClickSelection": True,
                                                                    "enableCellTextSelection": True,
                                                                    "ensureDomOrder": True,
                                                                    "suppressCellFocus": True,
                                                                    "animateRows": False,
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                    xxl=5,
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={"margin": "1%"},
                                ),
                                label="Network anomaly versions comparison",
                                tab_id="network-anomaly-tabs-compare-versions",
                            ),
                        ],
                        id="network-anomaly-tabs",
                    ),
                    style={"margin": "1%"},
                ),
            ],
        ),
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
        return (
            {"visibility": "hidden"},
            {"visibility": "hidden"},
            {"visibility": "hidden"},
        )

    return (
        {"visibility": "initial"},
        {"visibility": "initial"},
        {"visibility": "initial"},
    )


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
    Output("network-anomaly-history-table", "rowData", allow_duplicate=True),
    State("network-anomaly-table", "selectedRows"),
    Input("network-anomaly-visualize-button", "n_clicks"),
    prevent_initial_call="initial_duplicate",
)
def network_anomaly_detail_visualization_button_clicked(rows, n_clicks):
    if n_clicks is None:
        return []

    desc = rows[0].get('Description')
    return network_anomaly_api.get_network_anomalies(subset=False, network_anomaly_description=desc)
    # return symptom_api.get_symptoms(subset=False, incident_id=incident_id)

    # row = rows[0]
    # return network_anomaly_api.get_network_anomalies(
    #     subset=False, network_anomaly_description=row.get("Description")
    # )


@service.app.callback(
    Output("symptom-table", "rowData"),
    State("network-anomaly-history-table", "selectedRows"),
    Input("network-anomaly-inspect-button", "n_clicks"),
)
def network_anomaly_detail_inspect_button_clicked(rows, n_clicks):
    if n_clicks is None or n_clicks == 0:
        return no_update
    
    incident_id = rows[0].get('ID')
    return symptom_api.get_symptoms(subset=False, incident_id=incident_id)


@service.app.callback(
    Output("network-anomaly-add-new-version-input-auth", "value"),
    Output("network-anomaly-add-new-version-input-state", "value"),
    Output("new-version-symptom-table-current", "rowData", allow_duplicate=True),
    Output("network-anomaly-tabs", "active_tab", allow_duplicate=True),
    Input("network-anomaly-add-new-version-button", "n_clicks"),
    State("network-anomaly-table", "selectedRows"),
    prevent_initial_call="initial_duplicate",
)
def network_anomaly_detail_inspect_button_add_new_vesion(n_clicks, rows):

    if n_clicks is None or n_clicks == 0:
        return no_update, no_update, no_update, no_update

    # Get last version
    history = network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=rows[0].get("Description")
    )
    history.sort(key=lambda x: x["Version"])

    # TODO: Get symptom IDs from the Incident
    incident_id = rows[0].get('ID')
    symptoms = symptom_api.get_symptoms(subset=False, incident_id=incident_id)

    return (
        history[-1]["Author Name"],
        history[-1]["State"],
        symptoms,
        "network-anomaly-tabs-new-version",
    )


# Add version section callbacks


@service.app.callback(
    Output("network-anomaly-history-table", "rowData", allow_duplicate=True),
    Output("network-anomaly-tabs", "active_tab", allow_duplicate=True),
    Input("network-anomaly-add-new-version-submit", "n_clicks"),
    State("network-anomaly-table", "selectedRows"),
    State("network-anomaly-history-table", "rowData"),
    State("network-anomaly-add-new-version-input-auth", "value"),
    State("network-anomaly-add-new-version-input-state", "value"),
    State("new-version-symptom-table-current", "rowData"),
    prevent_initial_call="initial_duplicate",
)
def network_anomaly_new_vesion_submit(
    n_clicks, rows, selectedRows, n_auth, n_state, n_symptoms
):
    # Initial callback
    if n_clicks is None:
        return no_update, no_update

    # Get last version
    history = network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=rows[0].get("Description")
    )
    history.sort(key=lambda x: x["Version"])
    out = history[-1]

    out["Version"] += 1
    out["Author Name"] = n_auth
    out["State"] = n_state

    success = network_anomaly_api.create_new_network_anomaly_version(out["ID"], out, n_symptoms)

    return (
        network_anomaly_detail_visualization_button_clicked(rows, 1),
        "network-anomaly-tabs-details",
    )


@service.app.callback(
    Output("new-version-symptom-table-current", "rowData", allow_duplicate=True),
    Input("network-anomaly-add-new-version-del-sympt", "n_clicks"),
    State("new-version-symptom-table-current", "rowData"),
    State("new-version-symptom-table-current", "selectedRows"),
    prevent_initial_call="initial_duplicate",
)
def network_anomaly_new_vesion_delete_symptom(n_clicks, rowData, selectedRows):
    # Initial callback
    if n_clicks is None or len(selectedRows) == 0:
        return no_update

    # TODO call also the related API
    for r in selectedRows:
        del rowData[rowData.index(r)]

    return rowData


@service.app.callback(
    Output("new-version-symptom-table-search", "rowData"),
    Input("network-anomaly-add-new-version-search-sympt", "n_clicks"),
    State("date-input-start", "value"),
    State("date-input-end", "value"),
    State("time-input-start", "value"),
    State("time-input-end", "value"),
    prevent_initial_call="initial_duplicate",
)
def network_anomaly_new_vesion_search_symptoms(
    n_clicks,
    start_date,
    end_date,
    start_time,
    end_time,
):
    # Initial callback
    if n_clicks is None or start_date is None or end_date is None or start_time is None or end_time is None:
        return no_update

    start = f"{start_date}T{start_time}"
    end = f"{end_date}T{end_time}"
    symptoms = symptom_api.get_symptoms(subset=False, start_time=start, end_time=end)

    return symptoms

@service.app.callback(
    Output("new-version-symptom-table-current", "rowData", allow_duplicate=True),
    Input("network-anomaly-add-new-version-add-sympt", "n_clicks"),
    State("new-version-symptom-table-search", "selectedRows"),
    State("new-version-symptom-table-current", "rowData"),
    prevent_initial_call="initial_duplicate",
)
def network_anomaly_new_vesion_add_symptoms(
    n_clicks,
    selected_rows,
    initial_rows,
):
    # Initial callback
    if n_clicks is None or len(selected_rows)==0:
        return no_update
    
    # TODO call also the related API

    return initial_rows + selected_rows


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
        subset=False, network_anomaly_description=row.get("Description")
    )

    avail_vers = [
        {"label": f"Version {k['Version']}", "value": k["Version"]}
        for k in annotation_history
    ]

    return avail_vers, avail_vers


@service.app.callback(
    Output("network-anomaly-compare-author-v1", "children"),
    Output("network-anomaly-compare-state-v1", "children"),
    Output("compare-symptom-table-v1", "rowData"),
    Input("network-anomaly-table", "selectedRows"),
    Input("network-anomaly-compare-input-v1", "value"),
)
def network_anomaly_compare_versions_data_v1(rows, selection):
    if rows is None or len(rows) == 0 or selection is None:
        return "Author:", "State:", []

    annotation_history = network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=rows[0].get("Description")
    )

    curr_version = [k for k in annotation_history if k["Version"] == int(selection)][0]
    symptoms = symptom_api.get_symptoms(subset=False, incident_id=curr_version.get('ID'))

    return (
        f"Author: {curr_version['Author Name']}",
        f"State: {curr_version['State']}",
        symptoms,
    )


@service.app.callback(
    Output("network-anomaly-compare-author-v2", "children"),
    Output("network-anomaly-compare-state-v2", "children"),
    Output("compare-symptom-table-v2", "rowData"),
    Input("network-anomaly-table", "selectedRows"),
    Input("network-anomaly-compare-input-v2", "value"),
)
def network_anomaly_compare_versions_data_v2(rows, selection):
    if rows is None or len(rows) == 0 or selection is None:
        return "Author:", "State:", []
    
    annotation_history = network_anomaly_api.get_network_anomalies(
        subset=False, network_anomaly_description=rows[0].get("Description")
    )
    curr_version = [k for k in annotation_history if k["Version"] == int(selection)][0]
    symptoms = symptom_api.get_symptoms(subset=False, incident_id=curr_version.get('ID'))

    return (
        f"Author: {curr_version['Author Name']}",
        f"State: {curr_version['State']}",
        symptoms,
    )
