from dash import html, dcc
import dash_ag_grid as dag
import dash_bootstrap_components as dbc


layout = html.Div([
    html.H1("Symptoms"),
    html.Div(id='symptom-incident-data', children=[
        dbc.Row([html.H2("Incident Details")]),
        dag.AgGrid(
            id="symptom-incident-selected",
            className="ag-theme-alpine selection",
            # columnDefs=column_defs,
            rowData=[],
            columnSize="sizeToFit",
            style={"height": 400, "width": "100%"},
            dashGridOptions={
                'rowSelection': 'single', 
                'suppressRowClickSelection': True, 
                'enableCellTextSelection': True, 
                'ensureDomOrder': True,
                "suppressCellFocus": True, 
                "animateRows": False
            }
        ),
    ])
])

from callbacks import symptoms as symptoms_callbacks