import os
import sys

sys.path.append('helpers')
import excel_extractor

sys.path.append('database')
import handler


if __name__ == "__main__":

    academic_dict = {
        "Paper": os.path.join(os.path.dirname(__file__), "data_papers.xlsx"),
        "Effect": os.path.join(os.path.dirname(__file__), "data_effects.xlsx"),
    }

    database_handler = handler.DatabaseHandler()
    for table_name, excel_file in academic_dict.items():
        column_names, values = excel_extractor.ExcelDataExtractor.extract(excel_file)
        database_handler.insert_multiple_rows(table_name, column_names, values)
        database_handler.commit_changes()
