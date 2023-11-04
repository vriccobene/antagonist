# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /antagonist

# Install any needed packages specified in requirements.txt
ADD ./requirements.txt /antagonist/requirements.txt
RUN pip install --trusted-host pypi.python.org -r /antagonist/requirements.txt

# Copy the current directory contents into the container
COPY . /antagonist/

# Run app.py when the container launches
ENV PYTHONPATH "${PYTHONPATH}:/antagonist"
CMD ["python", "/antagonist/service.py"]
