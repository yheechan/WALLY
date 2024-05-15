# Download base image ubuntu 20.04
FROM ubuntu:20.04

# Set a directory for the source code
WORKDIR /root

# Update Ubuntu Software repository
RUN apt-get update && apt-get -y install --no-install-recommends \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-venv \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    zlib1g-dev \
    wget \
    curl \
    git \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*


# Install Python packages
RUN python3 -m pip install --upgrade pip

# Install pytest
RUN python3 -m pip install pytest

# Install coverage
RUN python3 -m pip install coverage

# Install pytest-cov
RUN python3 -m pip install pytest-cov

# Copy all the files to the container
COPY . .

# Permanently set the PATH in the container
ENV PATH="/root/framework/bin:${PATH}"
