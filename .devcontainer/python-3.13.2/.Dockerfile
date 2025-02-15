FROM python:3.13.2-slim-bookworm

# Get the latest version of things up and running
RUN apt-get update && \
    apt-get upgrade --yes --no-install-recommends && \
    apt-get install --yes curl git && \
    apt-get clean

# Install the latest version of pip
RUN pip install --upgrade pip
