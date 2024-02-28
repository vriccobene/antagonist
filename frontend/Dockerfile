# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /frontend

# Install any needed packages specified in requirements.txt
ADD ./requirements.txt /antagonist-frontend/requirements.txt
RUN pip install --trusted-host pypi.python.org -r /antagonist-frontend/requirements.txt

# Copy the current directory contents into the container
COPY . /antagonist-frontend/

# Run app.py when the container launches
ENV PYTHONPATH "${PYTHONPATH}:/frontend"
CMD ["python", "/antagonist-frontend/service.py"]
