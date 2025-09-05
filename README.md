## AviFluHunt Database and Tool  

**Frontend User Documentation**

---

#### Table of Contents
1. [Introduction](#introduction)  
2. [Getting Started](#getting-started)  
3. [User Interface Overview](#user-interface-overview)  
4. [Additional Notes](#additional-notes)
5. [Extra](#extra)

---

## 1. Introduction

AviFluHunt provides a **web-based interface** for avian flu researchers to:
- Filter data by location, date range, or host type.
- Query markers and their effects on hosts or drugs (according to literature).
- Build interesting analytics on markers, segments, and mutations.

The system is built to leverage **domain knowledge** (markers, effects, literature references, etc.) and is powered by a **Dockerized backend** to simplify setup and deployment.

---

## 2. Getting Started

For details on how to use AviFluHunt Docker, please visit [this link](https://github.com/DEIB-GECO/AviFluHunt/blob/main/docker_doc.md), then come back here!

1. **Access the Application**  
   Once Docker is running (using `docker compose up -d`), open your browser and navigate to the URL provided in the Docker logs (e.g., `http://localhost:8000`).

2. **Prepare Required Data Files**  
   - A `.fasta` file containing sequence data for analysis.  
   - A `.xls` metadata file following the structure of GISAID downloads.  
   - (Optional) Updated XLSX files containing domain knowledge if you set `update_also_knowledge=true` (details [here](https://github.com/DEIB-GECO/AviFluHunt/blob/main/docker_doc.md)).

3. **Verify Global Settings**  
   Before running queries, ensure the **Global Filters** (dates, locations) match the subset of data you expect to analyze.

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



### Queries

The queries are grouped into four **macro categories**. Select a macro group, then pick one of the listed queries from the dropdown.

<img width="990" height="733" alt="image" src="https://github.com/user-attachments/assets/ff1cc452-2ee0-4ee1-a3dc-609ef34e7dd4" />



### Global Settings

Global filters affect **all** queries you run. Use them to narrow your dataset by **location** and **date range**.

1. **Location**  
   - **Regions**: Select from a list of continents or large areas (e.g., Asia, Europe).  
   - **States**: Within a chosen region, optionally select specific states/provinces. If none are selected, **all** locations in that region are included.

2. **Date Range**  
   - Choose a **Start Date** and **End Date**. Only isolates collected within this date range are considered.

You can revisit the **Global Settings** panel anytime to adjust these filters. The **Global Settings Recap** displays your current selection.


### Taxonomy Tree

The **Taxonomy Tree** is an informational tool showing avian species in the database. It is generated based on:
- Automatically detected hosts in your dataset.  
- Supplemental taxonomy data (used if the automatic taxonomer fails to identify certain hosts).

---

## 4. Additional Notes

- **Performance**:  
  Large datasets (big `.fasta` or `.xls` files) may slow queries. Narrow your date range or location to improve performance.

- **Domain Knowledge Updates**:  
  If you change or add knowledge in the XLSX files (markers, effects, references), set `update_also_knowledge=true` in your `.env` file before restarting Docker to ensure the new knowledge is integrated.

- **Troubleshooting**:  
  - **No Results?** Check that your **Global Settings** (date range, location) include valid data.  
  - **Missing Markers/Hosts?** Confirm your metadata file follows a GISAID-like structure and `.fasta` file path is correct.  
  - **Taxonomy Issues?** Rare hosts may require manual addition to the fallback taxonomy data.

- **Further Assistance**:  
  Refer to [this documentation](https://github.com/DEIB-GECO/AviFluHunt/blob/main/docker_doc.md) for Docker commands and environment variable details.
  For additional support or to report a bug, open an issue on the project’s GitHub repository.

---

## 5. Extra

### Acknowledgements

We gratefully acknowledge all data contributors, i.e. the Authors and their Originating Laboratories responsible for obtaining the specimens, and their Submitting Laboratories that generated the genetic sequence and metadata and shared via the GISAID Initiative the data on which part of this research is based. 

The authors are grateful to Stefano Ceri, Alice Fusaro, and Edoardo Giussani for the fruitful discussions inspiring this research, and to Jana Penic for assisting with Influenza data preparation.


### Funding
The work was supported by Ministero dell'Università e della Ricerca (PRIN PNRR 2022 "SENSIBLE" project, n. P2022CNN2J), funded by the European Union, Next Generation EU, within PNRR M4.C2.1.1. 
Politecnico di Milano, CUP D53D23017400001; Università degli Studi di Milano, CUP G53D23006690001. See our [project's website](https://sensible-prin.github.io/)! 


### Citation

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
[https://github.com/DEIB-GECO/AviFluHunt](https://github.com/DEIB-GECO/AviFluHunt).
_Manuscript in preparation._
```

---

### Contact us

https://annabernasconi.faculty.polimi.it/

anna.bernasconi@polimi.it

Phone: +39 02 2399 3494
