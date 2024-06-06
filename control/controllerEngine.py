import threading
import serial
import time
import re


class Controller:
    def __init__(self, port, status_callback=None):
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
        self.new_p_value = ""
        self.new_i_value = ""
        self.new_d_value = ""

        self.read_pid_values = False
        self.r5_gain_value = 0  # P gain value
        self.r6_gain_value = 0  # I gain value
        self.r7_gain_value = 0  # D gain value

        self.autotune_mode = False
        self.start_autotune = False
        self.status_callback = status_callback

        self.lock = threading.Lock()

        self.r68_output = ""
        self.r65_output = ""

    def set_read_pid_values(self):
        with self.lock:
            self.read_pid_values = True

    def set_turn_off_flag(self):
        with self.lock:
            self.turn_off = True

    def set_manual_mode_flag(self, temp_value):
        with self.lock:
            self.start_manual = True
            self.temp_value = temp_value

    def set_start_autotune_flag(self):
        with self.lock:
            self.start_autotune = True

    def set_pid_flag(self, new_temp_entry, entry_p_value, entry_i_value, entry_d_value):
        with self.lock:
            self.start_pid = True
            self.temp_value = new_temp_entry
            self.new_p_value = entry_p_value
            self.new_i_value = entry_i_value
            self.new_d_value = entry_d_value

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
                    self.ser.write("$REG 63=0\r\n".encode())  # turn off fans
                    ack = self.read_response()
                    self.ser.write("$REG 2=0\r\n".encode())  # Send off value to controller
                    ack = self.read_response()  # store controller acknowledgement

                    if "REG 2=0" in ack and "?" not in ack:  # if controller ack contains right reg value and recognize command
                        self.is_running = False
                        self.manual_mode = False
                        self.cycle_mode = False
                        self.pid_mode = False
                        self.autotune_mode = False  # set all run flags to False
                        self.turn_off = False  # Reset flag to avoid continuous loop

                """Manual mode logic"""
                if self.start_manual:  # Check if user set manual run mode flag
                    self.start_fans()
                    if self.is_running:  # Check if controller is already running
                        self.ser.write("$REG 2\r\n".encode())  # ask controller the value of run register
                        ack = self.read_response()  # store controller acknowledgement

                        if "REG 2=1" in ack:  # check for manual mode value in controller's response
                            if self.write_temp_value():
                                self.start_manual = False  # Reset flag to avoid continuous loop
                        else:  # If controller is in another run mode
                            self.ser.write("$REG 2=1\r\n".encode())  # Sends run in manual command to controller
                            ack = self.read_response()  # store controller acknowledgement

                            if "REG 2=1" in ack:  # check ack for right reg value and data
                                self.cycle_mode = False
                                self.pid_mode = False
                                self.autotune_mode = False  # Set other flags to False
                                self.manual_mode = True  # Set manual_mode to True
                                if self.write_temp_value():
                                    self.start_manual = False  # Reset flag to avoid continuous loop
                    else:  # If controller is not running
                        self.ser.write("$REG 2=1\r\n".encode())  # Sends run in manual command to controller
                        ack = self.read_response()  # store controller acknowledgement

                        if "REG 2=1" in ack:  # check ack for right reg value and data
                            self.is_running = True
                            self.manual_mode = True  # Set running and manual_mode flags to True
                            if self.write_temp_value():
                                self.start_manual = False  # Reset flag to avoid continuous loop

                """autotune logic"""
                if self.start_autotune:
                    self.start_fans()

                    if not self.is_running:
                        self.ser.write("$REG 2=4\r\n".encode())
                        ack = self.read_response()
                        if "REG 2=4" in ack:
                            self.autotune_mode = True
                            self.is_running = True
                            self.update_status("Auto-tune starting")

                    if self.autotune_mode:
                        self.ser.write("$REG 2=4\r\n".encode())
                        ack = self.read_response()
                        if "REG 2=4" in ack:
                            self.manual_mode = False
                            self.pid_mode = False
                            self.cycle_mode = False

                        self.ser.write("$REG 1\r\n".encode())
                        ack = self.read_response()
                        parsed_ack = ack.strip()[-2:]

                        if "=" in parsed_ack:
                            self.update_status("Auto-tune running")
                        elif "11" in parsed_ack:
                            self.update_status("Auto-tune successful")
                            self.start_autotune = False
                            self.autotune_mode = False
                            self.turn_off = True
                        elif "12" in parsed_ack:
                            self.update_status("Auto-tune failed")
                            self.start_autotune = False
                            self.autotune_mode = False
                            self.turn_off = True

                """Read PID Values Logic"""
                if self.read_pid_values:
                    for i in range(5, 8):  # Loop over register numbers 5, 6, 7
                        self.ser.write(f"$REG {i}\r\n".encode())
                        ack = self.read_response().strip()
                        gain_value = self.extract_float(ack)
                        if i == 5:
                            self.r5_gain_value = gain_value
                        elif i == 6:
                            self.r6_gain_value = gain_value
                        elif i == 7:
                            self.r7_gain_value = gain_value
                    self.read_pid_values = False

                """PID logic"""
                if self.start_pid:
                    self.start_fans()

                    if self.is_running:
                        self.ser.write("$REG 2\r\n".encode())
                        ack = self.read_response()
                        if "REG 2=3" in ack:
                            # Already in PID mode
                            if self.write_pid_values():
                                self.start_pid = False
                        else:
                            # Not in PID mode, switch to PID mode
                            self.ser.write("$REG 2=3\r\n".encode())
                            ack = self.read_response()
                            if "REG 2=3" in ack:
                                self.manual_mode = False
                                self.cycle_mode = False
                                self.autotune_mode = False
                                self.pid_mode = True
                                if self.write_pid_values():
                                    self.start_pid = False
                    else:
                        # Controller is not running, start it and switch to PID mode
                        self.ser.write("$REG 2=3\r\n".encode())
                        ack = self.read_response()
                        if "REG 2=3" in ack:
                            self.is_running = True
                            self.pid_mode = True
                            if self.write_pid_values():
                                self.start_pid = False

            t_end = time.time()
            elapsed_time = t_end - t_start
            sleep_time = 0.5 - elapsed_time
            time.sleep(sleep_time)

    def extract_float(self, ack):
        pattern = r'[-+]?\d*\.\d+|[-+]?\d+'
        match = re.search(pattern, ack)
        if match:
            return float(match.group())
        else:
            return None

    def read_sensors(self):
        """Reads and store register 68 (Sensor D) and register 65 (Sensor A) data"""
        self.ser.write("$REG 68\r\n".encode())
        ack = self.read_response().strip()
        self.r68_output = self.extract_float(ack)
        print(self.r68_output)

        self.ser.write("$REG 65\r\n".encode())
        ack = self.read_response().strip()
        self.r65_output = self.extract_float(ack)
        print(self.r65_output)

    def start_fans(self):
        """Start fan PSU output to 5v"""
        self.ser.write("$REG 63=1\r\n".encode())
        ack = self.read_response()

    def read_response(self):
        response = b""
        while True:
            chunk = self.ser.read_until(b'\r\n')
            response += chunk
            if b'\r\n' in chunk:
                break
        return response.decode('ascii').strip()

    def update_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def write_pid_values(self):
        self.ser.write(f"$REG 5={self.new_p_value}\r\n".encode())
        ack = self.read_response()
        self.ser.write(f"$REG 6={self.new_i_value}\r\n".encode())
        ack = self.read_response()
        self.ser.write(f"$REG 7={self.new_d_value}\r\n".encode())
        ack = self.read_response()
        self.read_pid_values = True
        self.ser.write(f"$REG 4={self.temp_value}\r\n".encode())
        ack = self.read_response()
        return f"REG 4={self.temp_value}" in ack

    def write_temp_value(self):
        self.ser.write(f"$REG 4={self.temp_value}\r\n".encode())
        ack = self.read_response()
        return "?" not in ack and f"REG 4={self.temp_value}" in ack
