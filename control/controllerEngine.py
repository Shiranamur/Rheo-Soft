import threading
import serial
import time
import re
from database.datalogger import DatabaseLogger


class Controller:
    def __init__(self, port, status_callback=None):
        self.port = port
        self.baudrate = 115200
        self.ser = None

        self.database_logger = DatabaseLogger()
        self.database_logger.create_table()

        self.is_running = False  # Flag indicating that the controller is running in any mode
        self.turn_off = False  # used to signal the user wants to turn off the heating/cooling

        self.manual_mode = False  # flag indicating that the manual mode is currently in use or not
        self.temp_value = ""
        self.start_manual = False  # flag indicating if the user wants to start the temperature regulation in manual mode

        self.pid_mode = False
        self.start_pid = False
        self.new_p_value = ""
        self.new_i_value = ""
        self.new_d_value = ""

        self.read_pid_values = False
        self.r5_gain_value = 0  # P gain value
        self.r6_gain_value = 0  # I gain value
        self.r7_gain_value = 0  # D gain value

        self.autotune_started = False
        self.start_autotune = False
        self.status_callback = status_callback

        self.lock = threading.Lock()

        self.r68_output = ""
        self.r65_output = ""

        self.new_alarm_temp_flag = False
        self.r68_alarm_new_temp_high = None
        self.r68_alarm_new_temp_low = None
        self.r65_alarm_new_temp_high = None
        self.r65_alarm_new_temp_low = None

        self.cycle_mode = False
        self.start_cycle = False

        self.high_temp = None
        self.low_temp = None
        self.use_percentage = False
        self.percentage_threshold = 0
        self.time_btw_switchover = 0
        self.wanted_nb_cycle = 0
        self.switchover_number = 0
        self.current_nb_cycle = 0
        self.switchover_callback = 0

        self.fan_running = False

    def set_alarm_temps(self, r68_new_high_temp, r68_new_low_temp, r65_new_high_temp, r65_new_low_temp):
        with self.lock:
            if r68_new_high_temp:
                self.r68_alarm_new_temp_high = r68_new_high_temp
            else:
                self.r68_alarm_new_temp_high = None
            if r68_new_low_temp:
                self.r68_alarm_new_temp_low = r68_new_low_temp
            else:
                self.r68_alarm_new_temp_low = None
            if r65_new_high_temp:
                self.r65_alarm_new_temp_high = r65_new_high_temp
            else:
                self.r65_alarm_new_temp_high = None
            if r65_new_low_temp:
                self.r65_alarm_new_temp_low = r65_new_low_temp
            else:
                self.r65_alarm_new_temp_low = None

            self.new_alarm_temp_flag = True
            print(
                f"Alarm temps set: r68_high={self.r68_alarm_new_temp_high}, r68_low={self.r68_alarm_new_temp_low}, r65_high={self.r65_alarm_new_temp_high}, r65_low={self.r65_alarm_new_temp_low}")

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
            if new_temp_entry:
                self.temp_value = new_temp_entry
            else:
                self.temp_value = None
            if entry_p_value:
                self.new_p_value = entry_p_value
            else:
                self.new_p_value = self.r5_gain_value
            if entry_i_value:
                self.new_i_value = entry_i_value
            else:
                self.new_i_value = self.r6_gain_value
            if entry_d_value:
                self.new_d_value = entry_d_value
            else:
                self.new_d_value = self.r7_gain_value
            self.start_pid = True

    def connect_controller(self):
        self.ser = serial.Serial(self.port, self.baudrate, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)

    def start_engine_thread(self):
        threading.Thread(target=self.engine, daemon=True).start()

    def engine(self):
        while True:
            t_start = time.time()
            with self.lock:  # acquire mutex to avoid race condition
                self.read_sensors()
                self.read_alarm_reg()

                """turn_off logic"""
                if self.turn_off:  # check turn_off flag
                    self.ser.write("$REG 2=0\r\n".encode())  # Send off value to controller
                    ack = self.read_response()  # store controller acknowledgement

                    if "REG 2=0" in ack:  # if controller ack contains right reg value and recognize command
                        self.is_running = False
                        self.manual_mode = False
                        self.cycle_mode = False
                        self.pid_mode = False
                        self.autotune_mode = False  # set all run flags to False
                        self.turn_off = False  # Reset flag to avoid continuous loop
                        self.switchover_number = 0
                        self.current_nb_cycle = 0
                        self.switchover_callback = 0

                """Manual mode logic"""
                if self.start_manual:  # Check if user set manual run mode flag
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
                    self.ser.write("$REG 2=4\r\n".encode())
                    ack = self.read_response()
                    if "REG 2=4" in ack:
                        self.start_autotune = False
                        self.autotune_started = True
                if self.autotune_started:
                    self.read_autotune_value()

                """Read PID Values Logic"""
                if self.read_pid_values:
                    print("Reading PID values")
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
                        print(f"Read value for REG {i}: {gain_value}")
                    self.read_pid_values = False

                """PID logic"""
                if self.start_pid:
                    print("Set PID flag found, entering PID logic")
                    if self.is_running:
                        print("Controller already running")
                        self.ser.write("$REG 2\r\n".encode())
                        ack = self.read_response()
                        if "REG 2=3" in ack:
                            print(f"Controller already running in PID mode : {ack}")
                            # Already in PID mode
                            self.write_pid_values()
                            print("write pid function executed")
                            self.start_pid = False
                            print("start pid flag set to False")
                        else:
                            print(f"Controller running in another mode : {ack}")
                            # Not in PID mode, switch to PID mode
                            self.ser.write("$REG 2=3\r\n".encode())
                            ack = self.read_response()
                            if "REG 2=3" in ack:
                                print("Switching to PID mode")
                                self.manual_mode = False
                                self.cycle_mode = False
                                self.autotune_mode = False
                                self.pid_mode = True
                                self.write_pid_values()
                                print("write pid function executed")
                                self.start_pid = False
                                print("start pid flag set to False")
                    else:
                        # Controller is not running, start it and switch to PID mode
                        print("Controller not running... starting")
                        self.ser.write("$REG 2=3\r\n".encode())
                        ack = self.read_response()
                        print(f"Received ack for starting in PID mode: {ack}")
                        if "REG 2=3" in ack:
                            print("controller started in pid mode")
                            self.is_running = True
                            self.pid_mode = True
                            self.write_pid_values()
                            print("write pid function executed")
                            self.start_pid = False
                            print("start pid flag set to False")
                        else:
                            print("Failed to start controller in PID mode")

                """Alarm Logic"""

                if self.new_alarm_temp_flag:
                    self.write_alarm_temp_value()
                """Cycle logic"""
                if self.start_cycle:
                    if self.start_cycle:
                        self.cycle_basculement()

                if self.cycle_mode:
                    self.cycle_basculement()


                self.database_logger.log(self.r68_output, self.r65_output)

            t_end = time.time()
            elapsed_time = t_end - t_start
            sleep_time = 0.5 - elapsed_time
            # print(elapsed_time)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def set_cycle_mode_flag(self, high_temp, low_temp, use_percentage, percentage_threshold, tbs, cycle_nb):
        with self.lock:
            self.high_temp = high_temp
            self.low_temp = low_temp
            self.use_percentage = use_percentage
            self.percentage_threshold = percentage_threshold
            self.wanted_nb_cycle = cycle_nb
            self.time_btw_switchover = tbs
            self.start_cycle = True
            print(
                f"Cycle mode flag set with high_temp: {high_temp}, low_temp: {low_temp}, use_percentage: {use_percentage}, "
                f"percentage_threshold: {percentage_threshold}, time_btw_switchover: {tbs}, wanted_nb_cycle: {cycle_nb}")

    def set_temp_value(self, temp_value):
        self.ser.write(f"$REG 4={temp_value}\r\n".encode())
        ack = self.read_response()

    def write_alarm_temp_value(self):
        if self.r68_alarm_new_temp_high:
            self.ser.write(f"$REG 34 = {self.r68_alarm_new_temp_high}\r\n".encode())
            ack = self.read_response()
        if self.r68_alarm_new_temp_low:
            self.ser.write(f"$REG 33 = {self.r68_alarm_new_temp_low}\r\n".encode())
            ack = self.read_response()
        if self.r65_alarm_new_temp_high:
            self.ser.write(f"$REG 28 = {self.r65_alarm_new_temp_high}\r\n".encode())
            ack = self.read_response()
        if self.r65_alarm_new_temp_low:
            self.ser.write(f"$REG 27 = {self.r65_alarm_new_temp_low}\r\n".encode())
            ack = self.read_response()
        self.new_alarm_temp_flag = False

    def extract_float(self, ack):
        pattern = r'=(\-?\d+(\.\d+)?)'
        match = re.search(pattern, ack)
        if match:
            return float(match.group(1))
        else:
            print(f"Failed to extract float from ack: {ack}")
            return None

    def read_sensors(self):
        """Reads and store register 68 (Sensor D) and register 65 (Sensor A) data"""
        self.ser.write("$REG 68\r\n".encode())
        ack = self.read_response().strip()
        self.r68_output = self.extract_float(ack)
        # print(self.r68_output)

        self.ser.write("$REG 65\r\n".encode())
        ack = self.read_response().strip()
        self.r65_output = self.extract_float(ack)
        # print(self.r65_output)

    def stop_fan(self):
        self.ser.write("$REG 39=0\r\n".encode())
        ack = self.read_response()
        self.fan_running = False

    def start_fan(self):
        self.ser.write("$REG 39=1\r\n".encode())
        ack = self.read_response()
        self.ser.write("$REG 63=2\r\n".encode())
        ack = self.read_response()
        self.fan_running = True

    def read_response(self):
        response = b""
        while True:
            chunk = self.ser.read_until(b'\r\n')
            response += chunk
            if b'\r\n' in chunk:
                break
        return response.decode('ascii').strip()

    def write_pid_values(self):
        self.ser.write(f"$REG 5={self.new_p_value}\r\n".encode())
        ack = self.read_response()
        self.ser.write(f"$REG 6={self.new_i_value}\r\n".encode())
        ack = self.read_response()
        self.ser.write(f"$REG 7={self.new_d_value}\r\n".encode())
        ack = self.read_response()
        self.read_pid_values = True

        if self.temp_value:
            self.ser.write(f"$REG 4={self.temp_value}\r\n".encode())
            ack = self.read_response()

    def write_temp_value(self):
        self.ser.write(f"$REG 4={self.temp_value}\r\n".encode())
        ack = self.read_response()

    def read_autotune_value(self):
        self.ser.write("$REG 1\r\n".encode())
        ack = self.read_response().strip()
        if ack.startswith("REG 1="):
            reg_value = int(ack.split("=")[1])
            if (reg_value & (1 << 11)) != 0:
                self.status_callback = "Autotune complete"
                self.autotune_started = False
                self.ser.write("$REG 2=0\r\n".encode())
                ack = self.read_response()
            elif (reg_value & (1 << 12)) != 0:
                self.status_callback = "Autotune failed"
                self.autotune_started = False
                self.ser.write("$REG 2=0\r\n".encode())
                ack = self.read_response()
            else:
                self.status_callback = "Autotune in progress"

    def read_alarm_reg(self):
        self.ser.write("$REG 38\r\n".encode())
        ack = self.read_response().strip()
        if ack.startswith("REG 38="):
            reg_value = int(ack.split("=")[1])
            for i in range(8):
                if reg_value & (1 << i) != 0:
                    if not self.fan_running:
                        self.start_fan()
                else:
                    self.stop_fan()

    def cycle_basculement(self):
        # Si est en mode cycle est n'a pas atteint la limite du nombre de basculement
        if self.cycle_mode and self.current_nb_cycle < self.wanted_nb_cycle:
            print(f"Cycle basculement started. Current cycle: {self.current_nb_cycle}/{self.wanted_nb_cycle}, "
                  f"Switchover callback: {self.switchover_callback}")

            if self.switchover_callback == 1:
                if self.use_percentage:
                    pct_of_temp = self.high_temp * (self.percentage_threshold / 100)
                    if self.r68_output >= pct_of_temp:
                        self.switchover_callback = 2
                        self.switchover_number += 1
                        print(
                            f"Switching to callback 2. Current r68_output: {self.r68_output}, Threshold: {pct_of_temp}")
                else:
                    if self.r68_output >= self.high_temp:
                        self.switchover_callback = 2
                        self.switchover_number += 1
                        print(
                            f"Switching to callback 2. Current r68_output: {self.r68_output}, High Temp: {self.high_temp}")

            elif self.switchover_callback == 2:
                self.switchover_number += 1
                r = self.switchover_number / 2
                if r % self.time_btw_switchover == 0:
                    self.switchover_callback = 3
                    print(f"Switching to callback 3 after {self.time_btw_switchover} seconds")

            elif self.switchover_callback == 3:
                self.ser.write(f"$REG 4={self.low_temp}\r\n".encode())
                ack = self.read_response()
                self.switchover_callback = 4
                print(f"Set temperature to low_temp: {self.low_temp}. Ack: {ack}")

            elif self.switchover_callback == 4:
                if self.use_percentage:
                    pct_of_temp = self.low_temp * (1 + abs(self.percentage_threshold - 100) / 100)
                    if self.r68_output <= pct_of_temp:
                        self.switchover_callback = 5
                        self.switchover_number += 1
                        print(
                            f"Switching to callback 5. Current r68_output: {self.r68_output}, Threshold: {pct_of_temp}")
                else:
                    if self.r68_output <= self.low_temp:
                        self.switchover_callback = 5
                        self.switchover_number += 1
                        print(
                            f"Switching to callback 5. Current r68_output: {self.r68_output}, Low Temp: {self.low_temp}")

            elif self.switchover_callback == 5:
                self.switchover_number += 1
                r = self.switchover_number / 2
                if r % self.time_btw_switchover == 0:
                    self.switchover_callback = 6
                    print(f"Switching to callback 6 after {self.time_btw_switchover} seconds")

            elif self.switchover_callback == 6:
                self.ser.write(f"$REG 4={self.high_temp}\r\n".encode())
                ack = self.read_response()
                self.switchover_number = 1
                self.current_nb_cycle += 1
                print(
                    f"Set temperature to high_temp: {self.high_temp}. Ack: {ack}. Current cycle: {self.current_nb_cycle}")

        elif not self.cycle_mode:  # si n'est pas en mode cycle
            self.ser.write(f"$REG 2=3\r\n".encode())
            ack = self.read_response()
            print(ack)
            self.is_running = True
            self.ser.write(f"$REG 4={self.high_temp}\r\n".encode())
            ack = self.read_response()
            self.cycle_mode = True
            self.start_cycle = False
            self.switchover_callback = 1
            print(f"Cycle mode started. High temp set to {self.high_temp}. Ack: {ack}, switchover value = {self.switchover_callback}")

        # si la limite de basculement a été atteinte
        elif self.current_nb_cycle >= self.wanted_nb_cycle:
            self.turn_off = True
            self.current_nb_cycle = 0
            self.switchover_callback = 0
            self.switchover_number = 0
            print("Cycle mode completed. Turning off.")
