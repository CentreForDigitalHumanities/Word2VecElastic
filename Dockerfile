FROM docker.io/python:3.11
ENV PYTHONUNBUFFERED=1

WORKDIR /base
COPY requirements.txt /base/
RUN pip install -r requirements.txt