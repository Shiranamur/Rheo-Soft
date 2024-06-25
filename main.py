# main.py

import customtkinter as tk
from settings import AppSettings
from tabview import Tabview
from utils.autodetect import identify_devices
import redis
from datetime import datetime
import logging
import os
from data.redistest import start_logging_thread  # Import the new function

# Folder to store logs
LOG_FOLDER = 'logs'

# Ensure the log folder exists
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# Set up logging with date in the filename
log_filename = os.path.join(LOG_FOLDER, f'application_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Folder to store session data
SESSION_DATA_FOLDER = os.path.join('data', 'session_data')

# Ensure the folder exists
if not os.path.exists(SESSION_DATA_FOLDER):
    os.makedirs(SESSION_DATA_FOLDER)


class Application(tk.CTk):
    def __init__(self):
        logging.info("Initializing Application")
        super().__init__()
        self.title(AppSettings.title)
        self.geometry(AppSettings.default_geometry(self))

        # Identify devices and store the ports
        try:
            self.pump_port, self.controller_port = identify_devices()
            logging.info(f"Pump Port: {self.pump_port}, Controller Port: {self.controller_port}")
        except Exception as e:
            logging.error(f"Error identifying devices: {e}")

        self.tabview = Tabview(master=self, pump_port=self.pump_port, controller_port=self.controller_port)
        self.tabview.pack(fill=tk.BOTH, expand=True)
        logging.info("Application Initialized")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.save_data_to_csv()
        self.purge_redis_data()
        self.destroy()

    def save_data_to_csv(self):
        try:
            df = self.tabview.graph.fetch_data_from_redis(last_minutes=1440 * 7)  # Fetch data for the last 7 days
            if not df.empty:
                filename = os.path.join(SESSION_DATA_FOLDER,
                                        f"sensor_data_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
                df.to_csv(filename, index=False)
                logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data to CSV: {e}")

    def purge_redis_data(self):
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.flushall()
            logging.info("Redis memory purged.")
        except Exception as e:
            logging.error(f"Error during Redis purge: {e}")


if __name__ == "__main__":
    logging.info("Starting Application")
    start_logging_thread()  # Start the logging thread
    app = Application()
    app.mainloop()
    logging.info("Application Started")
