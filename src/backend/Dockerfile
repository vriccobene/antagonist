FROM python:3.12-slim-bookworm

WORKDIR /antagonist
ADD ./requirements.txt /antagonist/requirements.txt
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --trusted-host pypi.python.org -r /antagonist/requirements.txt

COPY . /antagonist/
# COPY /antagonist/.env /antagonist/.env

ENV PYTHONPATH "${PYTHONPATH}:/antagonist"
CMD ["python", "/antagonist/main.py"]