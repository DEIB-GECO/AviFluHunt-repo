import re
import sqlite3

import pandas as pd

# Load the Excel file
file_path = '/home/luca/Desktop/ThesisTODO/Database/data_scripts/papers_sheets/markers.xlsx'

# DB connection
conn = sqlite3.connect('thesis.db')
cursor = conn.cursor()


# Create table if it doesn't exists
command = f"""CREATE TABLE IF NOT EXISTS Marker (
              marker_id INTEGER PRIMARY KEY AUTOINCREMENT, 
              annotation_id INTEGER, position TEXT, allele TEXT,
              FOREIGN KEY (annotation_id) REFERENCES Annotation (annotation_id));"""
cursor.execute(command)


annotation_dict = {
    "M1": "M1",
    "M2": "M2",
    "NS-1": "NS-1",
    "NS-2": "NS-2",
    "NP": "NP",
    "PB2": "PB2",
    "PB1": "PB1",
    "PB1-F2": "PB1-F2",
    "PA": "PA",
    "HA1-5": "HA1",
    "HA2-5": "HA2",
    "NA-1": "NA",
}


# Function to check if a row exists in the database
def row_already_exists(a_id, pos, letter):
    try:
        cursor.execute(f"SELECT * FROM Marker WHERE "
                       f"annotation_id = ? AND position = ? AND allele = ?", (a_id, pos, letter))
        if cursor.fetchone():
            return True
    except sqlite3.OperationalError:
        return False


def get_annotation_id(name):
    try:
        cursor.execute("SELECT annotation_id FROM Annotation WHERE annotation_name = ?", (name,))
        return cursor.fetchall()
    except sqlite3.OperationalError:
        return -1


def extract_last_number(string):
    # Regular expression pattern to find the number between two letters
    pattern = r'[A-Za-z]([0-9]+)[A-Za-z]'

    # Search for the pattern in the string
    match = re.search(pattern, string)
    if match:
        # If pattern is found, extract the number
        return match.group(1)
    else:
        return None  # Return None if no match is found


# Insert data if it doesn't exist
excel = pd.read_excel(file_path, keep_default_na=False, na_values=['_'])
for index, row in excel.values:

    try:
        annotation_name = annotation_dict[row[:row.index(":")]]
    except KeyError:
        continue

    position = extract_last_number(row)
    allele = row[-1]

    annotation_id = int(get_annotation_id(annotation_name)[0][0])
    if not row_already_exists(annotation_id, position, allele):
        command = "INSERT INTO Marker (annotation_id, position, allele) VALUES (?, ?, ?)"
        cursor.execute(command, (annotation_id, position, allele))
conn.commit()
