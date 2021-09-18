FROM python:3.9-slim

# Print Python output immediately to console
ENV PYTHONBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN apt-get update -y && \
    apt-get upgrade -y && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./src /src
WORKDIR /src

# Default command to run new containers
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
