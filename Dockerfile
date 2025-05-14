FROM ubuntu:focal

# Update and Install Vim, Git, and Python
RUN yes | unminimize


RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8


# Set the timezone to New York
RUN ln -snf /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo "America/New_York" > /etc/timezone


RUN apt-get update && \
    apt-get install -y \
    vim \
    git \
    rsync \
    binutils \
    python3.9-dev \
    python3.9 \
    python3.9-venv


# Create a non-root user named "appuser"
RUN useradd -m -s /bin/bash pydev

# Set the working directory to the home directory of the "appuser"
WORKDIR /home/pydev

# Change ownership of the working directory to "pydev"
RUN chown -R pydev:pydev /home/pydev

# Create dir for mounted folder
RUN mkdir /home/pydev/pyMRI

# Create dir where data is stored on actual pet server
RUN mkdir -p /data8/data/

# Change ownership to "pydev"
RUN chown -R pydev:pydev /data8/data

# Switch to the non-root user
USER pydev

# Start bash shell by default
CMD ["/bin/bash"]
