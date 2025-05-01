# Perform a two-stage build - 
# Ref https://www.docker.com/blog/containerized-python-development-part-1/
FROM python:3.12 AS builder
# The full python image contains all the tools necessary for building.
COPY requirements.txt .
# Install dependencies.
# A local user directory, though suggested, is not used as it confuses VS Code
# when starting a container for development.
RUN python -m pip install -r requirements.txt

# Perform second stage
FROM python:3.12-slim
# The slim image allows our final image to be smaller.

# Install Sqlite3 as a utility for database actions.
RUN apt-get update && apt-get install -y sqlite3

# Keeps Python from generating .pyc files in the container.
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy in the dependencies from the builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy in the application code.
WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 1001 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["alembic", "upgrade", "head"]
