import sqlite3
import datetime


class DatabaseLogger:
    def __init__(self, db_file='database.db'):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            sensorD REAL,
            sensorA REAL
            )
        ''')
        self.conn.commit()

    def log(self, sensor_d, sensor_a):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO sensor_data (timestamp, sensorD, sensorA)
            VALUES (?, ?, ?)
            ''', (timestamp, sensor_d, sensor_a))
        self.conn.commit()

    def close(self):
        self.conn.close()
