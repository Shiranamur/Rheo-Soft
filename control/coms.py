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
            time.sleep(0.1)  # à ajuster

    def start_thread(self):
        thread = threading.Thread(target=self.connect_and_log, daemon=True)
        thread.start()

    def get_data(self):
        return self.data_queue.get()


class Controller:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = None
        self.read_r68_command = '$REG 68\r\n'
        self.read_r65_command = '$REG 65\r\n'
        self._r68_output = None
        self._r65_output = None

    def connect(self):
        self.ser = serial.Serial(self.port, self.baud_rate, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)
        if not self.ser.is_open:
            self.ser.open()

    def start_r68_thread(self):
        thread = threading.Thread(target=self.read_r68, daemon=True)
        thread.start()

    def read_r68(self):
        while True:
            if self.ser and self.ser.is_open:
                self.ser.write(self.read_r68_command.encode())
                time.sleep(0.1)
                r = self.ser.read_until(b'\r\n').decode().strip()
                self._r68_output = r[-7:] if r else "No Data!"
                print(self._r68_output)
                time.sleep(0.2)
            else:
                time.sleep(1)

    def start_r65_thread(self):
        thread = threading.Thread(target=self.read_r65, daemon=True)
        thread.start()

    def read_r65(self):
        while True:
            if self.ser and self.ser.is_open:
                self.ser.write(self.read_r65_command.encode())
                time.sleep(0.1)
                r = self.ser.read_until(b'\r\n').decode().strip()
                self._r65_output = r[-7:] if r else "No Data!"
                print(self._r65_output)
                time.sleep(0.2)
            else:
                time.sleep(1)

    def r68_output(self):
        return self._r68_output

    def r65_output(self):
        return self._r65_output


