# pumpFrame.py
import customtkinter as tk
from control.coms import Pump
from queue import Empty

class PumpFrame(tk.CTkFrame):
    def __init__(self, master, height, width, port):
        super().__init__(master, height=height, width=width)

        self.pump_port = port
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
