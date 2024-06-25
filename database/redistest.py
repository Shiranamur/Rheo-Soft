import valkey as redis
import datetime
import random
import time

class DataLogger:
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

# Function to generate random data
def generate_random_data():
    return random.randint(0, 100), random.randint(0, 100)

# Create an instance of DataLogger
logger = DataLogger()

# Main loop to generate and log data
while True:
    sensor_a, sensor_d = generate_random_data()
    logger.log(sensor_d, sensor_a)
    print(f"Logged data: sensor_a={sensor_a}, sensor_d={sensor_d}")
    time.sleep(0.5)
