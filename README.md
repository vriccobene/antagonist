# Antagonist
AnTagOnIst (<ins>An</ins>omaly <ins>Tag</ins>ging <ins>On</ins> h<ins>Ist</ins>orical data) is a Label Store for Network Anomaly Detection.

It's basically a tool that supports the visual analysis and the tagging of anomalies on  telemetry data.
This is done by providing a user-friendly interface to "Tag" anomalous data on multiple telemetry metrics and produce some metadata reflecting the semantic of those anomalies.

# What is a Network Anomaly?
In the context of this project, an anomaly is considered to be any event that could potentially be of concern in the execution of network services.
A network anomaly is a collection of symptoms.

More information on Symptoms, Network Anomalies and the format of information that is used in this project can be found in the following documents:
 - https://datatracker.ietf.org/doc/draft-netana-nmop-network-anomaly-semantics/
 - https://datatracker.ietf.org/doc/draft-netana-nmop-network-anomaly-lifecycle/

# Antagonist Architecture
![Antagonist Architecture](https://github.com/vriccobene/antagonist/blob/IETF120/images/antagonist_architecture.png)

# Installation / deployment instructions
The easiest way to get this running is by using Docker.
The following instructions are assuming you have Docker already installed on your system.

A docker compose file is provided as part of the project (under the docker directory).
The docker compose will spin up the following containers: 

 - grafana
 - influxDB
 - postgres-db
 - antagonist-core
 - antagonist-frontend
 - dashboard-manager

The current version of Antagonist stores information internally on PostgreSLQ.
In order to allow used to tag data it relies on Grafana, which is automatically connected through the docker compose with InfluxDB.

# Running a demo

## Where to get the data?
 If you want to run a demo, you can use this opensource data available in the following repository.
 
 Create the directory ./data/OmniAnomaly and inside that directory, run this command:

    git clone https://github.com/NetManAIOps/OmniAnomaly.git


## Prepare the data
After deploying the containers, it is required to add telemetry data into InfluxDB.
This can be done by using the provided script to load up the data. Instructions are provided in the following:

    cd demo
    python -m pip install -r requirements.txt
    python demo_preparation.py


## Tagging data using Grafana
The GUI (Graphic User Interface) is based on Grafana (https://github.com/grafana/grafana), an open source software used for data visualization.
The system relies on a Grafana native functionality called "Annotations", which allows the user to add annotations to timeseries data. These annotations are then queried using the Grafana REST API and enriched through the information added in the GUI by the user.

## Load up the dashboard on Grafana
Two pre-defined Grafana dashboards have to be load up on the system, which are located in docker/grafana/provisioning/dashboads/

They can be imported in Grafana, following the standard import procedure.


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
