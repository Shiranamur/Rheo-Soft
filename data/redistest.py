# redistest.py

import redis
import datetime
import threading
import time
import random

class ValkeyLog:
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db)

    def log(self, sensor_d, sensor_a):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            'timestamp': timestamp,
            'sensor_a': sensor_a,
            'sensor_d': sensor_d
        }
        key = self.r.incr("data_counter")
        self.r.hset(f"data_{key}", mapping=data)

def generate_and_log_random_values():
    valkey_log = ValkeyLog()
    while True:
        sensor_a = random.uniform(0, 100)  # Generate a random float between 0 and 100
        sensor_d = random.uniform(0, 100)  # Generate a random float between 0 and 100
        valkey_log.log(sensor_d, sensor_a)
        time.sleep(0.5)

def start_logging_thread():
    logging_thread = threading.Thread(target=generate_and_log_random_values)
    logging_thread.daemon = True
    logging_thread.start()
