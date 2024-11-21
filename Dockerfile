# Use Debian as the base image
FROM debian:bookworm-slim

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    bash \
    git \
    iputils-ping \
    curl \
    openssh-server \
    python3 \
    python3-pip \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*  # Clean up the apt cache to reduce image size

# Create the privilege separation directory
RUN mkdir -p /run/sshd && chmod 0755 /run/sshd

# Generate SSH host keys
RUN ssh-keygen -A

# Configure SSH server settings
RUN echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# Create group and user 'customer0'
RUN groupadd -r observers && useradd -ms /usr/bin/git-shell -G observers customer0

# Copy your custom files into the container
COPY srv /srv
RUN chmod -R 755 /srv

# Experimental section. Users should be added by the django app
# Set up SSH authorized keys for the 'customer0' user
USER customer0
RUN mkdir -p /home/customer0/.ssh && \
    echo "paste pubkey here" > /home/customer0/.ssh/authorized_keys && \
    chmod 700 /home/customer0/.ssh && \
    chmod 600 /home/customer0/.ssh/authorized_keys && \
    chown -R customer0:observers /home/customer0/.ssh

# Initialize a bare Git repository for 'watchman0'
RUN mkdir -p /home/customer0/repos/watchman0.git && \
    cd /home/customer0/repos/watchman0.git && \
    git init --bare

# Copy Git hooks
RUN cp -r /srv/git/hooks/* /home/customer0/repos/watchman0.git/hooks/
# End of experimental section

# Switch back to the root user
USER root
# Expose SSH port
EXPOSE 22

# Run the SSH server in the foreground
CMD ["/usr/sbin/sshd", "-D", "-e"]
