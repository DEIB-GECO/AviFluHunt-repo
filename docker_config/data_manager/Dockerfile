FROM ubuntu:latest

WORKDIR /app

# Install build-essential and other required tools in one step
RUN apt-get update && \
    apt-get install -y build-essential curl dos2unix && \
    rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN curl -sLo miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh

# Add Miniconda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Add conda-forge and bioconda channels, prioritize conda-forge
RUN conda config --add channels conda-forge && \
    conda config --add channels bioconda && \
    conda config --set channel_priority strict

# Install MAFFT and set Python version using conda
RUN conda install -y mafft python=3.12 && \
    conda clean --all --yes

# Install Python dependencies
ADD data_manager/requirements.txt /app/
RUN pip install --timeout=6000 --no-cache-dir -r requirements.txt

# Copy all application code
COPY ./data_manager /app

# Convert backend.sh to Unix format and make it executable
RUN dos2unix data_manager_init.sh && \
    chmod +x data_manager_init.sh

# Run the backend script
CMD ["./data_manager_init.sh"]
