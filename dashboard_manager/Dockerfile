# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /dashboard_manager

# Install any needed packages specified in requirements.txt
ADD ./requirements.txt /dashboard_manager/requirements.txt
RUN apt update

RUN pip install --trusted-host pypi.python.org -r /dashboard_manager/requirements.txt

# Copy the current directory contents into the container
COPY . /dashboard_manager/

# Run app.py when the container launches
ENV PYTHONPATH "${PYTHONPATH}:/dashboard_manager"
CMD ["python", "/dashboard_manager/service.py"]
