import re
import sqlite3
import sys

sys.path.append('../../helpers')
import excel_extractor

sys.path.append('../../database')
import handler

import pandas as pd

# Load the Excel file
markers_data_file = 'data_markers.xlsx'

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


if __name__ == '__main__':
    column_names, values = excel_extractor.ExcelDataExtractor.extract(markers_data_file)
    excel = pd.read_excel(markers_data_file, keep_default_na=False, na_values=['_'])
    database_handler = handler.DatabaseHandler()
    for index, row in values:

        allele = row[-1]
        position = extract_last_number(row)

        try:
            annotation_name = annotation_dict[row[:row.index(":")]]
        except KeyError:
            continue

        try:
            annotation = database_handler.get_rows("Annotation", ["annotation_name"], (annotation_name,))[0]
        except IndexError:
            continue

        database_handler.insert_row("Marker",
                                    ["position", "allele", "annotation_id"],
                                    [position, allele, annotation["annotation_id"]])
        database_handler.commit_changes()
