# Antagonist Label Store
AnTagOnIst (<ins>An</ins>omaly <ins>Tag</ins>ging <ins>On</ins> h<ins>Ist</ins>orical data) is a Label Store for Network Anomaly Detection.
It's basically a tool that supports the visual analysis and the tagging of anomalies on  telemetry data.

This is done by providing a user-friendly interface to "Tag" anomalous data on multiple telemetry metrics and produce some metadata reflecting the semantic of those anomalies.

## What is a Network Anomaly?
In the context of this project, an anomaly is considered to be any event that could potentially be of concern in the execution of network services.
A network anomaly is a collection of symptoms.

More information on Symptoms, Network Anomalies and the format of information that is used in this project can be found in the following documents:
 - https://datatracker.ietf.org/doc/draft-ietf-nmop-network-anomaly-lifecycle/
 - https://datatracker.ietf.org/doc/draft-ietf-nmop-network-anomaly-semantics/

# Deployment instructions
The easiest way to get this running is by using [Docker](https://www.docker.com/).
The following instructions are assuming you have Docker already installed on your system.

A [Docker Compose](https://docs.docker.com/compose/) file is provided as part of the project.
 
The docker compose will spin up the following containers: 

 - antagonist-backend
 - antagonist-frontend
 - [*influxdb*](https://www.influxdata.com/)
 - [*postgres*](https://www.postgresql.org/)

The current version of Antagonist stores information internally on PostgreSLQ.

Note: if running behind a proxy, you might need to use `docker build --build-arg HTTPS_PROXY="http://proxy.example.com:3128" -t antagonist:latest .` or similar. See the DockerDocs [here](https://docs.docker.com/engine/cli/proxy/) for options.

Before using docker, you need to make sure a ".env" file is create and 
populated based on your needs and local setup (an example is provided).

# Running a demo
Running a demo with synthetic data in order to familiarize with the system is easy.
Just follow the instructions provided in [demo instructions](./src/demo/run.sh)

IMPORTAN NOTE: Instructions as they are only work for Linux. 
The creation of a link is needed, if on Windows, please perform an equivalent configuration.


# Disclaimer
The user of this project is solely responsible for the misuse or unlawful use of this software and content. Authors disclaim any responsibility for harm, loss, or damage resulting from such misuse. This includes but is not limited to unlawful activities, data loss, or adverse effects of any kind. Hacking and cybersecurity laws vary by jurisdiction. By engaging with this project, you agree to take full responsibility for your actions.

## Important Note
There are several actions recommended before running this code in production, including but not limited to removing all the passwords in clear.
