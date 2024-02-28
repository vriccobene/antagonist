import uuid
import pandas as pd

network_anomaly_data = [
    {"ID": "6ff58573-c1a1-4dc7-ab55-7b7f346d1070", "Description": "January 2023 - 01", "Author Name": "Vince", "Version": 1, "State": "Forecasted"},
    {"ID": "a500d322-7dae-43fe-b4d9-51e1791e6b39", "Description": "March 2023 - 01", "Author Name": "Antonio", "Version": 1, "State": "Potential"},
    {"ID": "a500d322-7dae-43fe-b4d9-51e1791e6b39", "Description": "March 2023 - 01", "Author Name": "Wanting", "Version": 2, "State": "Confirmed"},
    {"ID": "7573b20a-5420-4750-8ee2-3caf87c2a860", "Description": "April 2023 - 01", "Author Name": "Thomas", "Version": 1, "State": "Confirmed"},
    {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Vince", "Version": 1, "State": "Potential"},
    {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Wanting", "Version": 2, "State": "Potential"},
    {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Wanting", "Version": 3, "State": "Potential"},
    {"ID": "a56a0336-699c-4ad6-b6fd-dfdc589f6b7b", "Description": "September 2023 - 01", "Author Name": "Vince", "Version": 4, "State": "Discarded"},
    {"ID": "1154face-711b-44b8-81cc-28032383c584", "Description": "November 2023 - 01", "Author Name": "Alex", "Version": 1, "State": "Confirmed"},
]

column_subset = ["ID", "Description"]
column_fullset = ["ID", "Description", "Author Name", "Version", "State"]


def get_network_anomalies(subset=True, network_anomaly_id=None):
    columns = column_subset if subset else column_fullset
    df = pd.DataFrame.from_dict(network_anomaly_data)
    filter_df = df.drop_duplicates(subset=columns)
    filter_df = df[df.ID == network_anomaly_id] if network_anomaly_id else filter_df
    return filter_df[columns].to_dict('records')


def get_network_anomaly_col_def(subset=True):
    columns = column_subset if subset else column_fullset
    column_defs = [{"field": columns[0], "checkboxSelection": True, "sortable": True, "filter": True}]
    column_defs.extend([{"field": field, "sortable": True, "filter": True} for field in columns[1:]])
    return column_defs


def get_network_anomaly(network_anomaly_id: uuid.UUID):
    return next(net_anomaly for net_anomaly in network_anomaly_data if net_anomaly.get('ID') == network_anomaly_data)
