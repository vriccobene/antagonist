# Antagonist
AnTagOnIst (<ins>An</ins>omaly <ins>Tag</ins>ging <ins>On</ins> h<ins>Ist</ins>orical data) is a tool that supports the visual analysis and the tagging of anomalies on  telemetry data.
This is done by providing a user-friendly interface to "Tag" anomalous data on multiple telemetry metrics and produce some metadata reflecting the semantic of those anomalies.

# What is a Network Anomaly?
In the context of this project, an anomaly is considered to be any event that could potentially be of concern in the execution of network services.
A network anomaly is a collection of symptoms

# Where to get the data
Different data sources can be used to demonstrate or run the project.
An example data set is provided here (instructions on how to set it up are provided below).
This is based on some open source data available on the web related to network monitoring.
This data is stored on InfluxDB and can be tagged using Grafana (see instructions below).
InfluxDB and Grafana are currently provided as example: the system can integrate with any timeseries data and graphical tool, as it provides an abstract API.

The main API is based on 2 IETF drafts:
 - https://datatracker.ietf.org/doc/draft-netana-nmop-network-anomaly-semantics/
 - https://datatracker.ietf.org/doc/draft-netana-nmop-network-anomaly-lifecycle/


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
After deploying the c ontainers, you will need to add the data to InfluxDB.
This can be done by using theprovided script to load up the data (script provided in the scripts directory).

    cd scripts/data_load
    python -m pip install -r requirements.txt
    python influxdb_load_data.py

If you want to use that script to load up the data, data file is avaialable here: https://github.com/cisco-ie/telemetry/blob/master/2/bgpclear.csv.zip

(But it should be relatively easy to work with different data).

## Tagging data using Grafana
The GUI (Graphic User Interface) is based on Grafana (https://github.com/grafana/grafana), an open source software used for data visualization.
The system relies on a Grafana native functionality called "Annotations", which allows the user to add annotations to timeseries data. These annotations are then queried using the Grafana REST API and enriched through the information added in the GUI by the user.

## Load up the dashboard on Grafana
Two pre-defined Grafana dashboards have to be load up on the system, which are located in docker/grafana/provisioning/dashboads/

They can be imported in Grafana, following the standard import procedure.

# Data for the Demo

 ## Where to get the data?
 For the initial demo we are taking some opensource data from the following repository:
 
 Create the directory ./data/OmniAnomaly and inside that directory, run this command

    git clone https://github.com/NetManAIOps/OmniAnomaly.git


# Disclaimer
The User of this project is solely responsible for the misuse or unlawful use of this software and Content. 
Authors disclaim any responsibility for harm, loss, or damage resulting from such misuse. 
This includes but is not limited to unlawful activities, data loss, or adverse effects of any kind. 
Hacking and cybersecurity laws vary by jurisdiction. 
By engaging with this project, you agree to take full responsibility for your actions.


# Important Note
There are several actions recommended before running this code in production. Some of them are listed below:

- Replace Flask REST with a proper HTTP Server
- Remove passwords and tokens from the configuration files and fill them with proper mechanisms
- ...
