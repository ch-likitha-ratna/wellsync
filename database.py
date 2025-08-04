import mysql.connector
from mysql.connector import Error
from config import Config
import logging

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=True
            )
            if self.connection.is_connected():
                logging.info("Successfully connected to MySQL database")
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            self.connection = None
    
    def execute_query(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
            
            cursor.close()
            return result
        except Error as e:
            logging.error(f"Database error: {e}")
            return None
    
    def execute_many(self, query, params_list):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            result = cursor.rowcount
            cursor.close()
            return result
        except Error as e:
            logging.error(f"Database error: {e}")
            return None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("MySQL connection closed")

# Global database instance
db = Database()