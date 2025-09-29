# Ubuntu 24.04 LTS base image on 26 Sept 2025
FROM ubuntu:latest@sha256:353675e2a41babd526e2b837d7ec780c2a05bca0164f7ea5dbbd433d21d166fc

WORKDIR /app

# Install essential tools
RUN apt-get update && \
    apt-get install -y build-essential curl dos2unix && \
    rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN curl -sLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Set up channels: only conda-forge and bioconda, no defaults
RUN conda config --remove channels defaults || true && \
    conda config --add channels conda-forge && \
    conda config --add channels bioconda && \
    conda config --set channel_priority strict

# Install Python and MAFFT (avoid triggering conda-anaconda-tos)
RUN conda tos accept --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --channel https://repo.anaconda.com/pkgs/r && \
    conda install -y python=3.13 mafft && \
    conda clean --all --yes

# Copy source code
COPY ./data_manager/requirements.txt /app

# Install Python dependencies
RUN pip install --timeout=6000 -r requirements.txt

# Copy source code
COPY ./data_manager /app

# Fix line endings and set permissions
RUN dos2unix data_manager_init.sh && \
    chmod +x data_manager_init.sh

# Set the entrypoint
CMD ["./data_manager_init.sh"]
