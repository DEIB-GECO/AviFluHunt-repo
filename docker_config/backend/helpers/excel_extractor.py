import pandas as pd


class ExcelDataExtractor:

    @staticmethod
    def extract(file_path, sheet_name=0):
        """
        Extract column names and their values from an Excel file.

        :param file_path: Path to the Excel file.
        :param sheet_name: The name or index of the sheet to load. Default is the first sheet.
        :return: A tuple containing a list of column names and a dictionary of column names with their values.
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl',
                               keep_default_na=False, na_values=['_'])
            column_names = df.columns.tolist()
            values = [tuple(row) for row in df.itertuples(index=False, name=None)]
            return column_names, values
        except Exception as e:
            print(f"Error processing file: {e}")
            return [], {}
