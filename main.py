# main.py
import customtkinter as tk
from settings import AppSettings
from tabview import Tabview
from utils.autodetect import identify_devices  # Import the identify_devices function
import logging
from datetime import datetime
import threading

# Generate the log file name with the desired format
log_filename = datetime.now().strftime("log_%d_%m_%Y_%H%M.log")

# Configure the logging settings
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

def log_active_threads_info():
    """Logs detailed information about all active threads in the program"""
    active_threads = threading.enumerate()
    logging.info("Number of active threads: %d", len(active_threads))
    for thread in active_threads:
        logging.info(
            "Thread Name: %s, Thread ID: %s, Is Daemon: %s, Is Alive: %s",
            thread.name,
            thread.ident,
            thread.daemon,
            thread.is_alive()
        )

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

        # Log the active threads info
        log_active_threads_info()


if __name__ == "__main__":
    print("Starting Application")
    app = Application()
    app.mainloop()
    print("Application Started")

    # Log the active threads info after the application starts
    log_active_threads_info()
