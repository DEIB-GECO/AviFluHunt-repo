## AviFluHunt Database and Tool  

**Docker Environment Documentation**

---

### Table of Contents
[System Requirements](#system-requirements)  
[Directory Structure](#directory-structure)  
[Configuration Files](#configuration-files)  
[Building and Running Containers](#building-and-running-containers)  
[Managing Containers](#managing-containers)  
[Environment Variables](#environment-variables)  
[Troubleshooting and FAQs](#common-issues-and-troubleshooting)

---

This project utilizes Docker and Docker Compose to create a portable, reproducible environment for avian flu data analysis. 
The Docker setup packages all dependencies and scripts into containers, allowing researchers to focus on analysis without worrying about setup.

### System Requirements
- **Operating System**: Windows, macOS, or Linux  
- **Docker Version**: 20.10 or later  
- **Docker Compose Version**: v2.0 or later  
- **Minimum Disk Space**: 5GB  
- **Recommended RAM**: 8GB or higher

---

### Directory Structure
```
project-root/
│
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Custom build instructions for the app
├── .env                         # Environment-specific variables (user-supplied)
├── data/                        # Input files (FASTA, metadata)
├── knowledge/                   # XLSX files for domain knowledge (optional)
├── app/                         # Application source code (Flask backend, UI frontend)
└── README.md                    # Project overview and usage
```

---

### Quick start

- From [https://github.com/DEIB-GECO/AviFluHunt/](https://github.com/DEIB-GECO/AviFluHunt/), download the code (e.g., as a ZIP archive)
- From the terminal, reach the docker_config subfolder
- Open and edit the `.env` file by adding the paths of the sequences and metadata files (note that big files will require long processing times).
  An example configuration file is:
```env
fasta_file=/absolute/path/to/your/sequences.fasta
metadata_file=/absolute/path/to/your/metadata.xls
update_also_knowledge=true
```
- Open the Docker application (installation guidelines on [https://docs.docker.com/get-started/get-docker/](https://docs.docker.com/get-started/get-docker/))
- From the terminal, run the following: (the first will possibly require at least 20mins even for small datasets)
```bash
docker compose build
docker compose up -d
```
- Open the application on localhost:8501

---

### Configuration Files

#### `docker-compose.yml`
Defines multiple services:
- **backend**: Main computation engine for the app.
- **frontend**: Web interface served to users.
- **db**: Database container (if needed).

#### `.env`
User-defined file placed in the root directory with absolute paths to necessary data files and configuration flags.

Example:
```env
fasta_file=/absolute/path/to/your/sequences.fasta
metadata_file=/absolute/path/to/your/metadata.xls
update_also_knowledge=true
```

---

### Building and Running Containers

#### **Initial Build**
```bash
docker compose build
```
This builds the containers according to the `Dockerfile`.

#### **Starting Containers**
```bash
docker compose up -d
```
- The `-d` flag runs containers in detached (background) mode.
- After startup, access the frontend at `http://localhost:8000` (or your configured port).

#### **Shutting Down**
```bash
docker compose down
```
Stops and removes all containers in the project.

---

### Managing Containers

#### **Check Running Containers**
```bash
docker ps
```

#### **Check All Containers (including stopped)**
```bash
docker ps -a
```

#### **Remove All Containers from This Project**
If using a custom project name (e.g., `avian_flu`):
```bash
docker rm -f $(docker ps -aq --filter "label=com.docker.compose.project=avian_flu")
```

#### **Run Only One Container**
```bash
docker compose up -d service_name
```
Replace `service_name` with the actual name (e.g., `frontend`, `backend`).

---

### Environment Variables
Defined in `.env` file:

| Variable               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `fasta_file`           | **Absolute path** to the `.fasta` file. Used for segment/dna analysis.      |
| `metadata_file`        | **Absolute path** to the `.xls` file. Must match GISAID format.             |
| `update_also_knowledge` | `true` or `false`. Updates DB with knowledge from `knowledge/` XLSX files. |

**Notes:**
- Paths **must be absolute**.
- `update_also_knowledge=true` is recommended for the first run or after updating knowledge files.

---

### Troubleshooting and FAQs
| Problem                        | Solution                                                    |
|-------------------------------|--------------------------------------------------------------|
| Container fails to start      | Run `docker compose logs` to check error logs.               |
| No results in UI              | Verify correctness of `.fasta` and `.xls` paths.             |
| Database not updating         | Set `update_also_knowledge=true` and restart.                |
| Docker too slow               | Narrow scope using Global Filters (region/date) in frontend. |


**Q: Do I need to rebuild after updating the `.env` file?**  
A: No. Just restart the containers:
```bash
docker compose down && docker compose build && docker compose up -d
```

**Q: Can I add custom markers or knowledge?**  
A: Yes. Add XLSX files to `knowledge/` and set `update_also_knowledge=true`.

**Q: Can I run this on a server?**  
A: Yes, deploy on any system with Docker installed. Configure port mapping as needed.



