import json
from layouts import index as index_layout
import app as service
import url_manager as url_manager

home_url = "localhost:8050"
service.app.layout = index_layout.layout


if __name__ == "__main__":
    service.app.run_server(debug=True)
