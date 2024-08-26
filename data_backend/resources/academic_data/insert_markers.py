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


def create_marker(marker_string):

    allele = marker_string[-1]
    position = extract_last_number(marker_string)

    try:
        annotation_name = annotation_dict[marker_string[:marker_string.index(":")]]
    except KeyError:
        return None

    try:
        annotation = database_handler.get_rows("Annotation", ["annotation_name"], (annotation_name,))[0]
    except IndexError:
        return None

    markers = database_handler.get_rows(
        "Marker",
        ["annotation_id", "position", "allele"],
        (annotation["annotation_id"], position, allele,))

    if markers: return markers[0]["marker_id"]

    return database_handler.insert_row(
        "Marker",
        ["annotation_id", "position", "allele", "name"],
        [annotation["annotation_id"], position, allele, f"{annotation_name}:{position}{allele}"])


def create_marker_group(group):
    markers = database_handler.get_rows("MarkerGroup", ["marker_group_id"], (group,))
    if markers: return markers[0]["marker_group_id"]
    return database_handler.insert_row("MarkerGroup", ["marker_group_id"], [group])


if __name__ == '__main__':

    file_path = 'data_markers_aggregated.xlsx'
    df = pd.read_excel(file_path)

    database_handler = handler.DatabaseHandler()

    for _, row in df.iterrows():

        marker = row['marker']
        paper_doi = row['paper_doi']
        effect_full = row['effect_full']
        marker_group_id = row['marker_group_id']
        subtype_name = row['subtype_name']

        # Create Marker (if, not exists), return marker_id
        marker_id = create_marker(marker)

        # Create Marker Group (if, not exists), return marker_group_id
        group_id = create_marker_group(marker_group_id)

        try:

            # Find Paper id from Doi
            paper_id = database_handler.get_rows("Paper", ["doi"], (paper_doi,))[0]["paper_id"]

            # Find Effect id from Effect Type
            effect_id = database_handler.get_rows("Effect", ["effect_full"], (effect_full,))[0]["effect_id"]

            # Find Subtype id from Subtype Name
            subtype_id = database_handler.get_rows("Subtype", ["name"], (subtype_name,))[0]["subtype_id"]

            if marker_id is not None:

                # Create Entry in MarkerToGroup
                database_handler.insert_row("MarkerToGroup",
                                            ["marker_id", "marker_group_id"], [marker_id, group_id])

                # Create Entry in MarkerGroupPaperAndEffect
                database_handler.insert_row("MarkerGroupPaperAndEffect",
                                            ["marker_group_id", "paper_id", "effect_id"],
                                            [group_id, paper_id, effect_id])

                # Create Entry in MarkerGroupToSubtype
                database_handler.insert_row("MarkerGroupToSubtype",
                                            ["subtype_id", "marker_group_id"],
                                            [subtype_id, group_id])

        except IndexError:
            continue

    database_handler.commit_changes()

