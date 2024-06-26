# valkey.py

import redis
import datetime


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
        print(f'logged value {sensor_d}, {sensor_a}, {timestamp}, with key {key}')
