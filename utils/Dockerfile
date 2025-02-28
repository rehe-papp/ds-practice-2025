# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
# Both the utils and src folders will be mounted as volumes, please see docker-compose.yaml
WORKDIR /app

# Install the Python dependencies
RUN pip install grpcio-tools==1.60.0

# Set the command to run the container
CMD python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./yourprotofile.proto
