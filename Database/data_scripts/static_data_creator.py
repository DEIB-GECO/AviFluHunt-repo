"""
Module Name: static_data_creator.py
Author: Luca Cassenti
Contact: luca.cassenti@mail.polimi.it

Description:
    This module handles the creation and population of database tables with data from Excel files.
    It includes functionality to process Excel data and interact with a database.

    The module includes the following functionalities:
    - Parsing Excel files and extracting data
    - Creating database tables
    - Populating database tables with data from Excel files
"""
import database_handler as dh

# If running as a script, provide an entry point
if __name__ == "__main__":

    referenceSegmentMetadata = {
        "table_name": "ReferenceSegment",
        "table_dict": {
            "reference_id": "INTEGER PRIMARY KEY",
            "serotype_id": "INTEGER",
            "segment_type": "TEXT",
            "dna_fasta": "TEXT",
            "protein_fasta": "TEXT"
        },
        "table_connections": ", FOREIGN KEY (serotype_id) REFERENCES Serotype(serotype_id)",
        "table_signature": [1, 2],
        "excel": "/home/luca/Desktop/ThesisTODO/Database/data_scripts/static_sheets/reference_segment.xlsx"
    }

    annotationMetadata = {
        "table_name": "Annotation",
        "table_dict": {
            "annotation_id": "INTEGER PRIMARY KEY",
            "annotation_name": "TEXT",
            "annotation_type": "INTEGER",
            "reference_id": "INTEGER",
            "start_pos": "INTEGER",
            "end_pos": "INTEGER"
        },
        "table_connections": ", FOREIGN KEY (reference_id) REFERENCES ReferenceSegment(reference_id)",
        "table_signature": [1, 2],
        "excel": "/home/luca/Desktop/ThesisTODO/Database/data_scripts/static_sheets/annotation.xlsx"
    }

    serotypeMetadata = {
        "table_name": "Serotype",
        "table_dict": {
            "serotype_id": "INTEGER PRIMARY KEY",
            "name": "TEXT"
        },
        "table_connections": "",
        "table_signature": [1],
        "excel": "/home/luca/Desktop/ThesisTODO/Database/data_scripts/static_sheets/serotype.xlsx"
    }

    # Instantiate DatabaseHandler object
    DBHandler = dh.DatabaseHandler()
    # DBHandler.database_from_excel(referenceSegmentMetadata)
    # DBHandler.database_from_excel(annotationMetadata)
    # DBHandler.database_from_excel(serotypeMetadata)
