import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

class MySQLDatabase:
    def __init__(self):
        self._host = os.getenv('DB_HOST', 'localhost')
        self._name = os.getenv('DB_NAME')
        self._user = os.getenv('DB_USER')
        self._password = os.getenv('DB_PASSWORD')
        self._connection = None

    def _connect(self):
        try:
            self._connection = mysql.connector.connect(
                host=self._host,
                database=self._name,
                user=self._user,
                password=self._password
            )
        except Error as e:
            print(f"[ERROR] Failed to connect to MySQL: {e}")
            sys.exit(1)


    def get_connection(self):
        if self._connection is None or not self._connection.is_connected():
            self._connect()
        return self._connection

    def close(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()

    def execute_query(self, query: str):
        cursor = self._connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def execute_query_with_params(self, query: str, params: tuple):
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()