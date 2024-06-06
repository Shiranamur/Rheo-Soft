import serial
import threading
import time
from queue import Queue


class Pump:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = None
        self.data_queue = Queue()

    def connect_and_log(self):
        self.ser = serial.Serial(self.port, self.baud_rate)
        while True:
            if self.ser and self.ser.in_waiting:
                pump_output = self.ser.readline().decode('ascii').strip()
                self.data_queue.put(pump_output)
            time.sleep(0.1)  # Adjust as needed

    def start_thread(self):
        thread = threading.Thread(target=self.connect_and_log, daemon=True)
        thread.start()

    def get_data(self):
        return self.data_queue.get()