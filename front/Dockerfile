# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update; apt-get -qq -y install curl jq python3-tk vim 
# RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install pip requirements
COPY requirements.txt .
RUN pip install --upgrade pip; python -m pip install -r requirements.txt

WORKDIR /app

COPY app /app


# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

CMD ["gunicorn", "cb:server", "--threads=4", "-b", ":7000"]
