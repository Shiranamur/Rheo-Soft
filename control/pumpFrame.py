import customtkinter as tk
from control.coms import Pump
from utils.autodetect import identify_devices
from queue import Empty


class PumpFrame(tk.CTkFrame):
    def __init__(self, master, height, width):
        super().__init__(master, height=height, width=width)

        self.serial_ports = identify_devices()
        self.pump_port, _ = self.serial_ports  # Unpack to get pump port

        self.pump = Pump(self.pump_port)
        self.pump.start_thread()

        self.pump_data_label = tk.CTkLabel(self, text="")
        self.pump_data_label.pack(pady=20)

        self.update_pump_data()

    def update_pump_data(self):
        try:
            pump_data = self.pump.get_data()
            if pump_data:
                self.pump_data_label.configure(text=pump_data)
        except Empty:
            pass

        self.after(1000, self.update_pump_data)
