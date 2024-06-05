import threading

import serial

import time

class Controller:
    def __init__(self, port):
        self.port = port
        self.baudrate = 115200
        self.ser = None

        self.is_running = False  # Flag indicating that the controller is running in any mode
        self.turn_off = False  # used to signal the user wants to turn off the heating/cooling

        self.manual_mode = False  # flag indicating that the manual mode is currently in use or not
        self.temp_value = ""
        self.start_manual = False  # flag indicating if the user wants to start the temperature regulation in manual mode

        self.cycle_mode = False
        self.start_cycle = False

        self.pid_mode = False
        self.start_pid = False

        self.autotune_mode = False
        self.start_autotune = False

        self.lock = threading.Lock()

        self.r68_output = ""
        self.r65_output = ""

    def set_turn_off_flag(self):
        with self.lock:
            self.turn_off = True

    def set_manual_mode_flag(self, temp_value):
        with self.lock:
            self.start_manual = True
            self.temp_value = temp_value

    def connect(self):
        self.ser = serial.Serial(self.port, self.baudrate, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)

    def start_engine_thread(self):
        threading.Thread(target=self.engine, daemon=True).start()
        print("engine thread started")

    def engine(self):
        print("engine starting")
        while True:
            t_start = time.time()
            with self.lock:  # acquire mutex to avoid race condition
                self.read_sensors()

                """turn_off logic"""
                if self.turn_off:  # check turn_off flag
                    print("turn_off called")
                    self.ser.write("$REG 2=0\r\n".encode())  # Send off value to controller
                    ack = self.read_response()  # store controller acknowledgement
                    print(ack)

                    if "REG 2=0" in ack and "?" not in ack:  # if controller ack contains right reg value and recognize command
                        self.is_running = False
                        self.manual_mode = False
                        self.cycle_mode = False
                        self.pid_mode = False
                        self.autotune_mode = False  # set all run flags to False
                        self.turn_off = False  # Reset flag to avoid continuous loop

                """start_manual logic"""
                if self.start_manual:  # Check if user set manual run mode flag
                    if self.is_running:  # Check if controller is already running
                        self.ser.write("$REG 2\r\n".encode())  # ask controller the value of run register
                        ack = self.read_response()  # store controller acknowledgement

                        if "REG 2=1" in ack:  # check for manual mode value in controller's response
                            self.ser.write(f"$REG 4={self.temp_value}\r\n".encode())  # Sends new wanted temp value
                            ack = self.read_response()  # stores response
                            if "?" not in ack and "REG 4=" in ack:  # If controller ack contains right reg value and recognize command
                                self.start_manual = False  # Reset flag to avoid continuous loop

                        else:  # If controller is in another run mode :
                            self.ser.write(f"$REG 2=1\r\n".encode())  # Sends run in manual command to controller
                            ack = self.read_response()  # store controller acknowledgement

                            if "REG 2=1" in ack:  # check ack for right reg value and data
                                self.manual_mode = True  # Set manual_mode to True
                                self.cycle_mode = False
                                self.pid_mode = False
                                self.autotune_mode = False  # Set other flags to False
                                self.ser.write(f"$REG 4={self.temp_value}\r\n".encode())  # Sends new wanted temp value
                                ack = self.read_response()  # store controller ack
                                if "?" not in ack and "REG 4=" in ack:  # If controller ack contains right reg value and recognize command
                                    self.start_manual = False  # Reset flag to avoid continuous loop

                    elif not self.is_running:  # If controller is not running
                        self.ser.write("$REG 2=1\r\n".encode())  # Sends run in manual command to controller
                        ack = self.read_response()  # store controller acknowledgement

                        if "REG 2=1" in ack:  # check ack for right reg value and data
                            self.is_running = True
                            self.manual_mode = True  # Set running and manual_mode flags to True
                            self.ser.write(f"$REG 4={self.temp_value}\r\n".encode())  # Sends new wanted temp value
                            ack = self.read_response()  # store controller ack

                            if "?" not in ack and "REG 4=" in ack:  # If controller ack contains right reg value and recognize command
                                self.start_manual = False  # Reset flag to avoid continuous loop
            t_end = time.time()
            elapsed_time = t_end - t_start
            sleep_time = 0.5 - elapsed_time
            time.sleep(sleep_time)

    def read_sensors(self):
        """Reads and store register 68 (Sensor D) and register 65 (Sensor A) data"""
        self.ser.write("$REG 68\r\n".encode())
        self.r68_output = self.read_response()
        print(self.r68_output)
        self.ser.write("$REG 65\r\n".encode())
        self.r65_output = self.read_response()
        print(self.r65_output)

    def read_response(self):
        response = b""
        while True:
            chunk = self.ser.read_until(b'\r\n')
            response += chunk
            if b'\r\n' in chunk:
                break
        return response.decode('ascii').strip()
