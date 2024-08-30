import sys

sys.path.append('../../helpers')
import excel_extractor

sys.path.append('../../database')
import handler


if __name__ == "__main__":

    academic_dict = {
        "ReferenceSegment": "data_reference_segment.xlsx",
        "Annotation": "data_annotation.xlsx",
        "Subtype": "data_subtype.xlsx",
        "Intein": "data_intein.xlsx"
    }

    database_handler = handler.DatabaseHandler()
    for table_name, excel_file in academic_dict.items():
        column_names, values = excel_extractor.ExcelDataExtractor.extract(excel_file)
        database_handler.insert_multiple_rows(table_name, column_names, values)
        database_handler.commit_changes()
