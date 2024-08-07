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

    paperMetadata = {
        "table_name": "Paper",
        "table_dict": {
            "paper_id": "INTEGER PRIMARY KEY",
            "title": "TEXT",
            "authors": "TEXT",
            "year": "INTEGER",
            "journal": "TEXT",
            "address": "TEXT",
            "doi": "TEXT"
        },
        "table_connections": "",
        "table_signature": [6],
        "excel": "/home/luca/Desktop/ThesisTODO/Database/data_scripts/papers_sheets/papers.xlsx"
    }

    effectMetadata = {
        "table_name": "Effect",
        "table_dict": {
            "effect_id": "INTEGER PRIMARY KEY",
            "effect_type": "TEXT",
            "host": "TEXT",
            "drug": "TEXT",
            "effect_full": "TEXT"
        },
        "table_connections": "",
        "table_signature": [4],
        "excel": "/home/luca/Desktop/ThesisTODO/Database/data_scripts/papers_sheets/effects.xlsx"
    }

    PEMMetadata = {
        "table_name": "PaperAndEffectOfMarker",
        "table_dict": {
            "paper_effect_marker_id": "INTEGER PRIMARY KEY",
            "marker_id": "INTEGER",
            "paper_id": "INTEGER",
            "effect_id": "INTEGER",
            "subtype": "TEXT",
            "in_vivo": "INTEGER",
            "in_vitro": "INTEGER",
        },
        "table_connections": ", FOREIGN KEY (marker_id) REFERENCES Marker(marker_id),"
                             " FOREIGN KEY (paper_id) REFERENCES Paper(paper_id),"
                             " FOREIGN KEY (effect_id) REFERENCES Effect(effect_id)",
        "table_signature": [1, 2, 3],
        "excel": "/home/luca/Desktop/ThesisTODO/Database/data_scripts/papers_sheets/pem.xlsx"
    }

    # Instantiate DatabaseHandler object
    DBHandler = dh.DatabaseHandler()
    #DBHandler.database_from_excel(paperMetadata)
    #DBHandler.database_from_excel(effectMetadata)
    #DBHandler.database_from_excel(PEMMetadata)
