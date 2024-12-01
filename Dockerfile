# Use Debian as the base image
FROM python:3.13-slim

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    bash \
    git \
    iputils-ping \
    curl \
    openssh-server \
    openssh-client \
    pipx \
    && rm -rf /var/lib/apt/lists/*  # Clean up the apt cache to reduce image size

######################
# Prepare GIT server #
######################

# Create the privilege separation directory
RUN mkdir -p /run/sshd && chmod 0755 /run/sshd

# Generate SSH host keys
RUN ssh-keygen -A

# Configure SSH server settings
RUN echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# Create group and user 'customer0'
RUN groupadd -r observers

# Copy your custom files into the container
COPY shell_scripts /srv
RUN chmod -R 755 /srv

######################
# Prepare App server #
######################
WORKDIR /app

# Install Poetry
RUN pipx install poetry
ENV PATH="$PATH:/root/.local/bin"

# Copy the app source code into the container
COPY poetry.lock pyproject.toml /app/
# Install the app dependencies
RUN poetry install

# Expose ports
EXPOSE 22
EXPOSE 8000

# Copy the rest of the app source code into the container
COPY . /app

# Set the environment variable to indicate that the app is running in a Docker container
ENV IS_DOCKER=true
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]
