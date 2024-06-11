# main.py
import customtkinter as tk
from settings import AppSettings
from tabview import Tabview
from utils.autodetect import identify_devices  # Import the identify_devices function


class Application(tk.CTk):
    def __init__(self):
        print("Initializing Application")
        super().__init__()
        self.title(AppSettings.title)
        self.geometry(AppSettings.default_geometry(self))

        # Identify devices and store the ports
        self.pump_port, self.controller_port = identify_devices()
        print(f"Pump Port: {self.pump_port}, Controller Port: {self.controller_port}")

        self.tabview = Tabview(master=self, pump_port=self.pump_port, controller_port=self.controller_port)
        self.tabview.pack(fill=tk.BOTH, expand=True)
        print("Application Initialized")


if __name__ == "__main__":
    print("Starting Application")
    app = Application()
    app.mainloop()
    print("Application Started")
