# Import necessary libraries
import pandas
import sqlite3


# Define a class for database interaction
class DatabaseHandler:

    """
    Class: DatabaseHandler
    Description: Handles the creation and population of database tables.
    """

    # Define class attributes
    conn = sqlite3.connect('thesis.db')
    cursor = conn.cursor()

    def __del__(self):
        self.conn.close()

    # Creates and populates db
    def database_from_excel(self, table_metadata):
        self.create_table(table_metadata["table_name"], table_metadata["table_dict"],
                          table_metadata["table_connections"])
        self.populate_table(table_metadata["table_name"], table_metadata["table_dict"],
                            table_metadata["table_signature"], table_metadata["excel"])
        self.conn.commit()

    # Define method for creating database tables
    def create_table(self, table_name, table_dict, table_connections):

        """
        Method: create_tables
        Description: Creates database tables for ReferenceSegment, Genes, Proteins, and Serotype.
        """

        command = \
            f"""CREATE TABLE IF NOT EXISTS {table_name}
              ({self.create_table_parameters_from_dict(table_dict)}
              {table_connections});"""
        self.cursor.execute(command)

    # Create the statement for the table attributes
    @staticmethod
    def create_table_parameters_from_dict(table_dict):

        """
        Method: create_table_parameters_from_dict
        Description: TODO
        """
        return ", ".join([f"{column_name} {column_attr}" for column_name, column_attr in table_dict.items()])

    # Define method for populating database tables with Excel data
    def populate_table(self, table_name, table_dict, table_signature, excel_file):

        """
        Method: populate_tables
        Description: Populates database tables with data from Excel files.
        """
        excel = pandas.read_excel(excel_file, keep_default_na=False, na_values=['_'])
        for row in excel.values:
            if not self.row_already_exists(table_name, table_dict, table_signature, row):
                command = f"""INSERT INTO {table_name} VALUES {tuple(row)}"""
                self.cursor.execute(command)

    def row_already_exists(self, table_name, table_dict, table_signature, row):

        # Compose search
        table_signature.sort()
        signature_search = ", ".join([f"{list(table_dict.keys())[column_index]} = ?" for column_index in table_signature])
        value_search = tuple([tuple(row)[index] for index in table_signature])

        # Check if data exists
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE {signature_search}", value_search)
            if self.cursor.fetchone():
                return True
        except sqlite3.OperationalError:
            return False

