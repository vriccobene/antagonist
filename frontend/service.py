import json
from layouts import index as index_layout
import app as service

home_url = "localhost:8050"
service.app.layout = index_layout.layout

if __name__ == "__main__":
    service.app.run(debug=True,host="0.0.0.0",port=8050)
