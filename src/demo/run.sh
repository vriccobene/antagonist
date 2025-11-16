# Create the virtual environment to run the demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Download the OmniAnomaly dataset from the following repository

if [ ! -d "OmniAnomaly" ]; then
    git clone https://github.com/NetManAIOps/OmniAnomaly.git
else
    echo "OmniAnomaly already exists, skipping clone."
fi

# Link the data models from backend in here
if [ ! -e "label_store" ]; then
    ln -s ../../backend/data_models/label_store/ label_store
else
    echo "label_store already exists, skipping link."
fi

# Start the script to load the data into InfluxDB
python simulate_telemetry.py # --data_path ./OmniAnomaly/data/processed_data
