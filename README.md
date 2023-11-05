# Antagonist
AnTagOnIst (<ins>An</ins>omaly <ins>Tag</ins>ging <ins>On</ins> h<ins>Ist</ins>orical data) is a tool that supports the visual analysis and the tagging of anomalies on timeseries data.

This is done by providing a user-friendly interface to "Tag" anomalous data on multiple telemetry metrics and produce some metadata reflecting the semantic of those anomalies.

# How does it work?
The GUI (Graphic User Interface) is based on Grafana (https://github.com/grafana/grafana), an open source software used for data visualization.
The system relies on a Grafana native functionality called "Annotations", which allows the user to add annotations to timeseries data. These annotations are then queried using the Grafana REST API and enriched through the information added in the GUI by the user.

# Where to get the data
Different data sources can be used to demonstrate or run the project. The most important thing is that the data needs to be in InfluxDB.

Within this project a script is provided to upload some toy time series data on InfluxDB. 
The data used by the script is downloadable from the following link: https://github.com/cisco-ie/telemetry

# Installation / deployment instructions
The easiest way to get this running is by using Docker.
The following instructions are assuming you have Docker already installed on your system.

## Prepare for the deployment
The preparation step requires the building of the docker image, by running the following instructions:

    cd antagonist
    docker_build -t antagonist:latest .

## Deploy
A docker compose file is provided as part of the project (under the docker directory).
That docker compose will spin up 4 containers: grafana, influxDB, antagonist, postgres.

## Prepare the data
After deploying the containers, you will need to add the data to InfluxDB.
This can be done by using the provided script to load up the data (script provided in the scripts directory).
If you want to use that script to load up the data, data file is avaialable here: https://github.com/cisco-ie/telemetry/blob/master/2/bgpclear.csv.zip

(But it should be relatively easy to work with different data, if you have some degree of familiarity with Grafana).

## Load up the dashboard on Grafana
A pre-defined Grafana dashboard has to be load up on the system, which is located in docker/grafana/provisioning/dashboads/
