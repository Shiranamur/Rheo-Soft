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


class Controller:
    def __init__(self, port):
        self.port = port
        self.baud_rate = 115200
        self.ser = None
        self.sequences = [[5, 5], [5, 50],[5, 5], [5, 50],[5, 5], [5, 50],[5, 5], [5, 50]]

        self.setpoint_boolean = 0
        self.end_of_sequences_boolean = 0

        self.read_r68 = '$REG 68\r\n'
        self.read_r65 = '$REG 65\r\n'
        self.end_command = '$REG 2=0\r\n'
        self.set_temp = ''

        self._r68_output = None
        self._r65_output = None
        self.setpoint_ack = None
        self.end_cmd_ack = None

        self.lock = threading.Lock()

    def connect(self):
        self.ser = serial.Serial(self.port, self.baud_rate, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)

    def start_cycle_thread(self):
        threading.Thread(target=self.read_cycle, daemon=True).start()

    def start_send_command_thread(self):
        threading.Thread(target=self.send_command, daemon=True).start()

    def read_cycle(self):
        while True:
            for seq in self.sequences:
                sleep_time = seq[0]
                temp = seq[1]
                time.sleep(sleep_time)
                with self.lock:
                    self.setpoint_boolean += 1
                    self.set_temp = f"$REG 4={temp}\r\n"
                    print(f"sent new temp command : {self.set_temp}; increment_var : {self.setpoint_boolean}")
            with self.lock:
                self.end_of_sequences_boolean += 1
                print("Cycle ended, setting end_of_sequences to True")
                break

    def read_response(self):
        response = b""
        while True:
            chunk = self.ser.read_until(b'\r\n')
            response += chunk
            if b'\r\n' in chunk:
                break
        return response.decode('ascii').strip()


    def send_command(self):
        while True:
            t_start = time.time()
            with self.lock:
                if self.setpoint_boolean > 0:
                    self.ser.write(self.read_r68.encode())
                    self._r68_output = self.read_response()
                    self.ser.write(self.read_r65.encode())
                    self._r65_output = self.read_response()
                    self.ser.write(self.set_temp.encode())
                    self.setpoint_ack = self.read_response()
                    self.setpoint_boolean -= 1
                elif self.end_of_sequences_boolean > 0:
                    self.ser.write(self.read_r68.encode())
                    self._r68_output = self.read_response()
                    self.ser.write(self.read_r65.encode())
                    self._r65_output = self.read_response()
                    self.ser.write(self.end_of_sequences_boolean)
                    self.end_cmd_ack = self.read_response()
                    self.end_of_sequences_boolean -= 1
                else:
                    self.ser.write(self.read_r68.encode())
                    self._r68_output = self.read_response()
                    self.ser.write(self.read_r65.encode())
                    self._r65_output = self.read_response()
            t_end = time.time()
            elapsed_time = t_end - t_start
            sleept_time = max(0, 1 - elapsed_time)
            time.sleep(sleept_time)




    # def send_command(self):
    #     while True:
    #         t_start = time.time()
    #
    #         self.ser.write(self.read_r68.encode())
    #         print(f"Read r68 command: {self.read_r68.strip()}")
    #         self._r68_output = self.read_response()
    #         print(f"Received response: {self._r68_output}")
    #
    #         self.ser.write(self.read_r65.encode())
    #         print(f"Read r65 command: {self.read_r65.strip()}")
    #         self._r65_output = self.read_response()
    #         print(f"Received response: {self._r65_output}")
    #
    #         # Ensure the lock is acquired before checking increment_var
    #         with self.lock:
    #             print(f"Before if: increment_var = {self.increment_var}, end_of_sequences = {self.end_of_sequences}")
    #             if self.increment_var == 1:
    #                 print("Inside if: starting if send_command statement")
    #                 self.ser.write(self.set_temp.encode())
    #                 print(f"Sent command: {self.set_temp.strip()}")
    #                 self.setpoint_ack = self.read_response()
    #                 print(f"Received new temp response: {self.setpoint_ack.strip()}")
    #                 self.increment_var = 0
    #                 if self.end_of_sequences:
    #                     self.ser.write(self.end_command.encode())
    #                     print(f"Sent end command: {self.end_command.strip()}")
    #                     self.end_cmd_ack = self.read_response()
    #                     print(f"Received response: {self.end_cmd_ack}")
    #                     self.end_of_sequences = False
    #
    #         t_end = time.time()
    #         elapsed_time = t_end - t_start
    #         s_time = max(0, 1 - elapsed_time)
    #         time.sleep(s_time)


