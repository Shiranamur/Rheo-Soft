import serial
import threading
import time


class Pump:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = None

    def connect_and_read(self):
        self.ser = serial.Serial(self.port, self.baud_rate)
        while True:
            if self.ser and self.ser.in_waiting:
                pump_output = self.ser.readline().decode('utf-8').strip()
            time.sleep(0.1)  # à ajuster 

    def thread_and_log(self):
        thread = threading.Thread(target=self.connect_and_read)
        thread.daemon = True  # This will allow the program to exit even if the thread is still running
        thread.start()




class Controller:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = serial.Serial(self.port, self.baud_rate, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)
