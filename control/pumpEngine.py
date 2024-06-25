import serial
import threading
import time
import queue

class Pump:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = None
        self.data_queue = queue.Queue()

    def connect_and_log(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate)
            while True:
                if self.ser and self.ser.in_waiting:
                    pump_output = self.ser.readline().decode('ascii').strip()
                    self.data_queue.put(pump_output)
                time.sleep(1)
        except (serial.SerialException, AttributeError):
            pass

    def start_thread(self):
        thread = threading.Thread(target=self.connect_and_log, daemon=True)
        thread.start()

    def get_data(self):
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None

    def is_connected(self):
        return self.ser and self.ser.is_open
