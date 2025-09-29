# Usage

## Data download
The app requires a pair of metadata and sequence files describing the input. Both files can be downloaded from GISAID's EpiFlu interface after the login.
- Download the metadata file as an Excel (.xls) file.
- Download the sequences as a DNA/RNA FASTA file. In the download dialog page, specify the FASTA header as "DNA Accession no. | Segment | Virus name | Isolate ID | Type" and select any desired segment.  

## Link to data source
Open the ".env" file and fill the values of variables "fasta_file" and "metadata_file" with the path of the downloaded metadata and sequence files in the.

## Application launch & database update

```
docker-compose up -d
```

## Erase/Recreate the database

```
docker volume rm avifluhunt_sqlite_data
```
