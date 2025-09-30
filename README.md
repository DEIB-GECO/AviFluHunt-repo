## AviFluHunt 

---

#### Table of Contents
1. [Introduction](#1-introduction)  
2. [Getting Started](#2-getting-started)  
3. [User Interface Overview](#3-user-interface-overview)  
4. [Additional Notes](#4-additional-notes)
5. [Acknowledgements](#5-acknowledgements)
6. [Funding](#6-funding)
7. [Citation](#7-citation)
8. [Contacts](#8-contacts)

---

## 1. Introduction

AviFluHunt provides a **web-based interface** for avian flu researchers to:
- Filter data by location, date range, or host type.
- Query markers and their effects on hosts or drugs (according to literature).
- Build interesting analytics on markers, segments, and mutations.
---

## 2. Getting Started

### System Requirements
- **Operating System**: Windows, macOS, or Linux  
- **Docker Version**: 20.10 or later  
- **Docker Compose Version**: v2.0 or later  
- **Minimum Disk Space**: 5GB  
- **Recommended RAM**: 8GB or higher

### Data Download 

The app requires a pair of metadata and sequence files describing your input. Both files can be downloaded from GISAID's EpiFlu interface after the login.
- Download the metadata: in the download panel, select "Isolates as XLS (virus metadata only".
- Download the sequences: in the download panel, select "Sequences (DNA) as FASTA", select the segments you want to analyse (or check the option "all" to download all segments), copy and paste the string "DNA Accession no. | Segment | Virus name | Isolate ID | Type" (without apices) as FASTA Header.

### Software Download 

Click on the Green button "Code" and donwload this repository as a ZIP file or through `git`. If the download is a compressed folder, unzip it. 

Lastly, download and install Docker Desktop (see installation guidelines at [https://docs.docker.com/get-started/get-docker/](https://docs.docker.com/get-started/get-docker/)).

### Software Configuration 
Open the ".env" file and fill the values of variables "fasta_file" and "metadata_file" with the **absolute path** of the files you just downloaded.

### Start AviFluHunt for the first time

1. Launch Docker Desktop.
2. Open a terminal, navigate to the directory containing the AviFluHunt software and this file.
3. Run the command `docker-compose up -d`. 

### Use of AviFluHunt 

1. **Access the Application**  
   Once Docker is running (using `docker compose up -d`), open your browser and navigate to [http://localhost:8501](http://localhost:8501). The app will be running in the background until you shut if off explicitly (see [Stop AviFluHunt](#stop-avifluhunt)).
2. **Verify Global Settings**  
   Before running queries, ensure the **Global Filters** (dates, locations) match the subset of data you expect to analyze.
3. **Choose a Query and Start Exploring**  
   Choose a group of queries and, from the top dropdown menu, select a query. Results are shown in the bottom right panel.

   For a breakdown of the interface, refer to the section [User Interface Overview](#3-user-interface-overview)

### Stop AviFluHunt

Open a terminal window in the AviFluHunt software directoy and run the command `docker-compose down`.

### Start AviFluHunt after the first time

This section applies if you have already shut down the application with `docker-compose down`. Otherwise, simply navigate to [http://localhost:8501](http://localhost:8501) to keep using the previous instance of AviFluHunt that is still running in the background. 

**Restart the app without input changes**: 
Edit the `.env` file and set the flag `update_also_knowledge` to `false` to speed-up the boot time. Then, open a terminal window in the AviFluHunt software directory and run the command `docker-compose build && docker-compose up -d`. 

**Restart the app with input changes**: 
Set the flag `update_also_knowledge` equal to `true` in the `.env` file and make sure the paths to the metadata and sequence files are still correct, or update them accordingly. Open a terminal window in the AviFluHunt software directory and run the command `docker-compose build && docker-compose up -d`. Notice that changes in the input files are additive, i.e., new isolates found in the input will be added to the isolates already present in the app's internal database. Isolates will never be removed from the app unless you erase the database (see [Erase AviFluHunt's database](#erase-avifluhunts-database)).


### Erase AviFluHunt's database

Open a terminal window in the AviFluHunt software directoy, stop the app with the command `docker-compose down`, then run `docker volume rm avifluhunt_sqlite_data`. This will delete any previously included sequence from the app. 


---

## 3. User Interface Overview

Here follows a breakdown of the main interface sections (refer to the screenshot below for an example):

<img width="8000" height="4018" alt="interface" src="https://github.com/user-attachments/assets/61d9e4b1-8fe0-4a88-912f-5bc7bf32318b" />

1. **Navigation Bar (Top-Right)**
   - **Taxonomy Tree**: View or hide the avian taxonomy tree.  
   - **Global Settings**: Open the global settings panel to change date ranges and geographic filters.  
   - **About**: General information about the project.

2. **Query Section (Top-Center)**
   - **Query Macro Group**: Select which set of queries you want to explore (Markers Effects, Markers, Markers and Hosts, Mutations).  
   - **Specific Query**: After choosing a macro group, select a query from the dropdown.

3. **Global Settings Recap (Top-Left Panel)**
   - Displays your current global filters (e.g., date range, selected geographical regions).

4. **Inputs for Each Query (Bottom-Left Panel)**
   - Depending on the query, you may need to specify additional parameters (e.g., marker name, effect type, host type).

5. **Results Panel (Center / Bottom)**
   - Shows query outputs in a table or graph form, often with an option to download the data (CSV file) or the graph (PNG file).



The **queries** are grouped into four **macro categories**. Select a macro group, then pick one of the listed queries from the dropdown.

<img width="990" height="733" alt="image" src="https://github.com/user-attachments/assets/ff1cc452-2ee0-4ee1-a3dc-609ef34e7dd4" />


**Global filters** affect all queries you run. Use them to narrow your dataset by location and date range.

1. **Location**  
   - **Regions**: Select from a list of continents or large areas (e.g., Asia, Europe).  
   - **States**: Within a chosen region, optionally select specific states/provinces. If none are selected, **all** locations in that region are included.

2. **Date Range**  
   - Choose a **Start Date** and **End Date**. Only isolates collected within this date range are considered.

You can revisit the **Global Settings** panel anytime to adjust these filters. The **Global Settings Recap** displays your current selection.

The **Taxonomy Tree** is an informational tool showing avian species in the database. It is generated based on:
- Automatically detected hosts in your dataset.  
- Supplemental taxonomy data at path `data_manager/resources/taxonomy/manual_tax.xlsx` (used if the automatic taxonomer fails to identify certain hosts).

---

## 4. Additional Notes

- **Performance**:  
  Large datasets (big `.fasta` or `.xls` files) may slow queries. Narrow your date range or location to improve performance.

- **Domain Knowledge Updates**:  
  If you change or add knowledge in the XLSX files (markers, effects, references), set `update_also_knowledge=true` in your `.env` file before restarting Docker to ensure the new knowledge is integrated.

- **Troubleshooting**:  
  - **No Results?** Check that your **Global Settings** (date range, location) include valid data.  
  - **Missing Markers/Hosts/Isolates?** 
      1. Confirm your metadata file follows a GISAID-like structure and your sequence file is a FASTA file with headers described as "DNA Accession no.|Segment|Virus name|Isolate ID|Type".
      2. Confirm the paths for the metadata and sequence files indicated in the `.env` file are correct. 
      3. Some hosts may not be automatically understood by the software. You can manually add definitions for those hosts by editing the file at `data_manager/resources/taxonomy/manual_tax.xlsx`; after that, open the `.env` file and set the flag `update_also_knowledge` to `true`, then restart the application with the commands `docker-compose down && docker-compose build && docker-compose up -d`.
---

## 5. Acknowledgements

We gratefully acknowledge all data contributors, i.e. the Authors and their Originating Laboratories responsible for obtaining the specimens, and their Submitting Laboratories that generated the genetic sequence and metadata and shared via the GISAID Initiative the data on which part of this research is based. 

The authors are grateful to Stefano Ceri, Alice Fusaro, and Edoardo Giussani for the fruitful discussions inspiring this research, and to Jana Penic for assisting with Influenza data preparation.

## 6. Funding
The work was supported by Ministero dell'Università e della Ricerca (PRIN PNRR 2022 "SENSIBLE" project, n. P2022CNN2J), funded by the European Union, Next Generation EU, within PNRR M4.C2.1.1. 
Politecnico di Milano, CUP D53D23017400001; Università degli Studi di Milano, CUP G53D23006690001. See our [project's website](https://sensible-prin.github.io/)! 


## 7. Citation

The AviFluHunt application has been created by 
```
Luca Cassenti, Tommaso Alfonsi, Anna Bernasconi
Dipartimento di Elettronica, Informazione e Bioingegneria
Politecnico di Milano
Via Ponzio 34/5 Milano
20133 Milano
Italy
```
Please, consider citing this work in your research as:

```
Luca Cassenti, Tommaso Alfonsi, Anna Bernasconi (2025).
AviFluHunt: a database and tool for flexible querying of avian influenza sequence data.
https://github.com/DEIB-GECO/AviFluHunt-repo.
[Manuscript in preparation]
```

---

## 8. Contacts

https://annabernasconi.faculty.polimi.it/

anna.bernasconi@polimi.it

Phone: +39 02 2399 3494