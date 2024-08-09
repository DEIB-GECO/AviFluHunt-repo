import os
import re
import sqlite3

db_file_path = os.path.join(os.path.dirname(__file__), "thesis.db")
db_create_file_path = os.path.join(os.path.dirname(__file__), "thesis.db.sql")


class DatabaseHandler:

    _instance = None

    def __init__(self):
        if DatabaseHandler._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.connection = self._create_connection()
            DatabaseHandler._instance = self

    def __del__(self):
        self.connection.close()

    @staticmethod
    def get_instance():
        if DatabaseHandler._instance is None:
            DatabaseHandler()
        return DatabaseHandler._instance

    @staticmethod
    def _create_connection():
        connection = sqlite3.connect(db_file_path)
        connection.row_factory = sqlite3.Row
        return connection

    def create_tables(self):
        with open(db_create_file_path) as file:
            sql_content = file.read()

        # Modify CREATE TABLE commands to include IF NOT EXISTS
        sql_content = re.sub(r'CREATE TABLE\s+(\w+)\s*{', r'CREATE TABLE IF NOT EXISTS \1 {', sql_content,
                             flags=re.IGNORECASE)

        cursor = self.connection.cursor()
        sql_commands = sql_content.split(';')
        for command in sql_commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        self.commit_changes()

    def insert_row(self, table_name, columns, values, commit=False):
        """
        Inserts a single row into the specified table.

        :param table_name: Name of the table.
        :param columns: List of column names.
        :param values: List of values corresponding to the columns.
        :param commit: Whether to commit the transaction.
        """
        placeholders = ', '.join(['?' for _ in columns])
        insert_command = (f'INSERT OR IGNORE INTO {table_name} ({", ".join(columns)}) '
                          f'VALUES ({placeholders})')

        cursor = self.connection.cursor()
        cursor.execute(insert_command, values)

        if commit:
            self.commit_changes()

        return cursor.lastrowid

    def insert_multiple_rows(self, table_name, columns, values_list, commit=False):
        """
        Inserts multiple rows into the specified table.

        :param table_name: Name of the table.
        :param columns: List of column names.
        :param values_list: List of tuples, where each tuple contains values corresponding to the columns.
        :param commit: Whether to commit the transaction.
        """
        placeholders = ', '.join(['?' for _ in columns])
        insert_command = (f'INSERT OR IGNORE INTO {table_name} ({", ".join(columns)}) '
                          f'VALUES ({placeholders})')

        cursor = self.connection.cursor()
        cursor.executemany(insert_command, values_list)

        if commit:
            self.commit_changes()

    def get_rows(self, table_name, columns, values):
        """
        Retrieves all rows from the specified table that match the given column-value pairs.

        :param table_name: Name of the table.
        :param columns: List of column names to match.
        :param values: List of values to match.
        :return: List of tuples, where each tuple represents a row matching the criteria.
        """
        if len(columns) != len(values):
            raise ValueError("The number of columns must match the number of values.")

        # Create a WHERE clause with placeholders
        where_clause = ' AND '.join([f'{col} = ?' for col in columns])
        select_command = f'SELECT * FROM {table_name} WHERE {where_clause}'

        cursor = self.connection.cursor()
        cursor.execute(select_command, values)
        rows = cursor.fetchall()

        return rows

    def row_exists(self, table_name, columns, values):
        """
        Checks if a row with the specified values exists in the table.

        :param table_name: Name of the table.
        :param columns: List of column names to match.
        :param values: List of values to match.
        :return: True if the row exists, False otherwise.
        """
        if len(columns) != len(values):
            raise ValueError("The number of columns must match the number of values.")

        # Create a WHERE clause with placeholders
        where_clause = ' AND '.join([f'{col} = ?' for col in columns])
        select_command = f'SELECT 1 FROM {table_name} WHERE {where_clause} LIMIT 1'

        cursor = self.connection.cursor()
        cursor.execute(select_command, values)
        result = cursor.fetchone()

        return result is not None

    def commit_changes(self):
        self.connection.commit()


if __name__ == "__main__":
    DatabaseHandler.get_instance().create_tables()
