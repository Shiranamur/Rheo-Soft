import serial
import threading


class Pump:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = serial.Serial(self.port, self.baud_rate)

    def connect(self):
        if self.port:
            threading.Thread(target=self.ser.open).start()

class Controller:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = serial.Serial(self.port, self.baud_rate, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)

