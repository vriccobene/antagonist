# Antagonist
**AnTagOnIst** (<ins>An</ins>omaly <ins>Tag</ins>ging <ins>On</ins> h<ins>Ist</ins>orical data) is a tool that supports the visual analysis and the tagging of anomalies on  telemetry data.
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
The easiest way to get this running is by using [Docker](https://www.docker.com/).
The following instructions are assuming you have Docker already installed on your system.

## Prepare for the deployment
The preparation step requires the building of the docker image, by running the following instructions:

```shell
# From the project's root directory
cd antagonist
docker build -t antagonist:latest .
```

Note: if running behind a proxy, you might need to use `docker build --build-arg HTTPS_PROXY="http://proxy.example.com:3128" -t antagonist:latest .` or similar. See the DockerDocs [here](https://docs.docker.com/engine/cli/proxy/) for options.

## Deploy
A [Docker Compose](https://docs.docker.com/compose/) file is provided as part of the project (under the project's [docker](./docker) folder).
That docker compose will spin up 4 containers: [*grafana*](https://grafana.com/), [*influxdb*](https://www.influxdata.com/), *antagonist*, and [*postgres*](https://www.postgresql.org/).

To launch the project stack:
```shell
# From the project's root directory
cd docker
docker compose up
```

Once the stack started, the Antagonist frontend is available at http://localhost:8050/. 
See below for how to tag data and work with the Antagonist framework.

## Prepare the data
After deploying the containers, you will need to add the data to InfluxDB.
This can be done by using the provided script to load up the data (script provided in the project's [scripts](./scripts) folder).

```shell
# From the project's root directory
cd scripts/data_load
python -m pip install -r requirements.txt
python influxdb_load_data.py
```

If you want to use that script to load up the data, a demo dataset is available at https://github.com/cisco-ie/telemetry/blob/master/2/bgpclear.csv.zip. 
You may use the following commands to get the demo dataset before running the above `influxdb_load_data.py` step:
```shell
# From the project's root directory
# If behind proxy, add the following argument to the curl command: --proxy proxy.example.com:3128 \
curl -L \
  -o ./data/bgpclear.csv.zip \
  --create-dirs \
  https://github.com/cisco-ie/telemetry/raw/refs/heads/master/2/bgpclear.csv.zip
unzip ./data/bgpclear.csv.zip -d ./data/
```

Note that it should be relatively easy to work with a different dataset.

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
