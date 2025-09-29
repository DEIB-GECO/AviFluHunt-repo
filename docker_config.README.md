# Avian Flu Data Analysis Docker Project

This repository provides a Dockerized environment tailored for flu researchers. It simplifies the setup for data analysis by encapsulating dependencies and configuration into a containerized workflow. This README covers the Docker commands, environment variables, and general setup for getting started.

## Prerequisites

- **Docker & Docker Compose:** Ensure you have Docker (v20.10+) and Docker Compose installed on your system.
- **.env File:** Create an `.env` file in the root of the repository (see below for required variables).

## Docker Commands

### Building the Docker Image

```bash
docker compose build
```

- **Note:** This build process can take several minutes.

### Starting the Docker Containers

```bash
docker compose up -d
```

- This command launches the containers in detached mode.

### Stopping the Docker Containers

```bash
docker compose down
```

- This stops and removes the containers, allowing you to cleanly shut down the environment.

### Listing All Containers

```bash
docker ps -a
```

- Use this command to list all containers (both running and stopped).

### Managing Containers

If you need to delete all containers created by this Docker project—for example, to reset the environment or to bring up only one container—consider the following options:

- **Remove All Project Containers:**
  Assuming your Docker Compose file sets a project name (e.g., `avian_flu`), you can remove all containers associated with it by running:
  ```bash
  docker rm -f $(docker ps -aq --filter "label=com.docker.compose.project=avian_flu")
  ```
  *Replace `avian_flu` with your actual project name if different.*

- **Start Only a Single Container:**
  If you wish to scale the service to only one container (e.g., if your compose file scales a service by default), you can use:
  ```bash
  docker compose up -d --scale app=1
  ```
  *Replace `app` with the correct service name as defined in your `docker-compose.yml`.*

## Environment Variables

The Docker container relies on an `.env` file placed in the root of the project. This file should include:

- **fasta_file:**
  The **absolute path** to the `.fasta` file required for DNA segment computation.

- **metadata_file:**
  The **absolute path** to the `.xls` file needed for DNA computation.
  *Important:* This file must follow the same structure as those provided when downloading data from GISAID. An example file is provided in the repository.

- **update_also_knowledge:**
  A flag set to either `true` or `false`.
  - **Usage:**
    - Set to `true` on the first run to initialize the database with domain knowledge about avian flu.
    - Set to `true` again whenever the XLSX files (which contain updated knowledge) are modified.
    - Keeping this flag on `true` consistently is supported; however, note that it may slow down performance.

### Domain Knowledge Files Included

The Docker container integrates various datasets and reference materials critical for avian flu analysis, including:

- **Markers and Marker Groups:**
  Definitions and groupings of genetic markers.
- **Effect of Markers:**
  Documentation on how specific markers impact analysis.
- **Literature of Origin of Effects:**
  References and literature that detail the origin of the observed effects.
- **Reference Segment Data from NCBI:**
  Curated segment data sourced from the NCBI database.
- **Annotations Info:**
  Detailed annotations relevant to the data analysis.
- **Subtypes:**
  Classification of different virus subtypes.
- **Inteins:**
  Information on inteins involved in the analysis.
- **Taxonomy:**
  Used as a fallback if the automatic taxonomer fails to identify some hosts (this setting should not be modified under normal circumstances).

## Final Notes

- **Ease of Use:**
  While the Docker setup is designed to be straightforward, ensure that all file paths in your `.env` file are absolute paths to avoid configuration errors.
- **For Flu Researchers:**
  This project is built to cater to the specific needs of flu research by combining a robust analysis environment with detailed domain data.

Feel free to raise any issues or suggest improvements via the repository's issue tracker.