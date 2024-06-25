# runtime_graph.py
import customtkinter as tk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from threading import Lock, Thread
import redis
import time
import logging

class GraphPage(tk.CTkFrame):
    def __init__(self, parent, height, width, last_minutes=15):
        super().__init__(parent, height=height, width=width)
        print(f"GraphPage initialized with: width={width}, height={height}")  # Debug statement
        self.last_minutes = last_minutes
        self.figure = Figure(figsize=(width/100, height/100), dpi=100)
        self.ax = self.figure.add_subplot(111)
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)

        self.x_data, self.y_data = self.get_initial_data()
        self.plot = self.ax.plot(self.x_data, self.y_data, label='Sensor D')[0]
        self.ax.set_ylim(0, 100)  # Adjust according to your sensor data range
        self.ax.set_xlim(datetime.now() - timedelta(minutes=self.last_minutes), datetime.now())

        self.ax.grid(which='major', axis='both', linestyle='--', color='grey', alpha=0.5)

        label = tk.CTkLabel(self, text="Live Sensor Data Plotting")
        label.pack(pady=10, padx=10)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.scale = tk.CTkSlider(self, from_=15, to=180, orientation="horizontal", command=self.update_minutes)
        self.scale.set(self.last_minutes)
        self.scale.pack(side=tk.BOTTOM, fill="none", expand=True)

        self.scrollbar = tk.CTkScrollbar(self, orientation="horizontal", command=self.update_start_time)
        self.scrollbar.pack(side=tk.BOTTOM, fill="none", expand=True)
        self.initialize_scrollbar()

        self.return_button = tk.CTkButton(self, text="Return to Current Time", command=self.return_to_current_time)
        self.return_button.pack(side=tk.BOTTOM, fill="none", expand=True)

        self.update_thread = Thread(target=self.run_update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def fetch_data_from_redis(self, start_time=None, last_minutes=15):
        with Lock():
            try:
                r = redis.Redis(host='localhost', port=6379, db=0)
                keys = r.keys('data_*')
                data_list = []
                for key in keys:
                    if r.type(key) == b'hash':  # Ensure the key is of hash type
                        data = r.hgetall(key)
                        timestamp = datetime.strptime(data[b'timestamp'].decode('utf-8'), "%Y-%m-%d %H:%M:%S")
                        if start_time is None or (
                                start_time <= timestamp <= start_time + timedelta(minutes=last_minutes)):
                            sensor_d = float(data[b'sensor_d'].decode('utf-8'))  # Changed to float
                            sensor_a = float(data[b'sensor_a'].decode('utf-8'))  # Changed to float
                            data_list.append((timestamp, sensor_d, sensor_a))
                df = pd.DataFrame(data_list, columns=['timestamp', 'sensor_d', 'sensor_a'])
                df.sort_values('timestamp', inplace=True)
                logging.info(f"Fetched {len(df)} rows from Redis")
                return df
            except Exception as e:
                logging.error(f"Error fetching data: {e}")
                return pd.DataFrame(columns=['timestamp', 'sensor_d', 'sensor_a'])

    def get_initial_data(self):
        df = self.fetch_data_from_redis(last_minutes=self.last_minutes)
        if not df.empty:
            return list(df['timestamp']), list(df['sensor_d'])
        else:
            now = datetime.now()
            x_data = [now - timedelta(minutes=self.last_minutes) + timedelta(seconds=i) for i in
                      range(0, self.last_minutes * 60, 60)]
            y_data = [0 for _ in range(len(x_data))]
            return x_data, y_data

    def update_minutes(self, value):
        self.last_minutes = int(value)
        self.update_graph()

    def update_start_time(self):
        value = int(self.scrollbar.get()[0] * 100)
        self.start_time = self.get_start_time() + timedelta(minutes=(value / 100) * (self.total_duration_minutes - self.last_minutes))
        self.update_graph()

    def initialize_scrollbar(self):
        df = self.fetch_data_from_redis(last_minutes=1440 * 2)  # Fetch data for the last 7 days
        if not df.empty:
            self.total_duration_minutes = int((df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 60)
            self.start_time = df['timestamp'].min()
            self.scrollbar.set(0, 0.1)  # Initial scrollbar position
        else:
            self.total_duration_minutes = 0
            self.start_time = datetime.now()

    def get_start_time(self):
        return self.start_time

    def return_to_current_time(self):
        self.start_time = datetime.now() - timedelta(minutes=self.last_minutes)
        self.update_graph()

    def update_graph(self):
        df = self.fetch_data_from_redis(start_time=self.get_start_time(), last_minutes=self.last_minutes)
        if not df.empty:
            self.x_data = list(df['timestamp'])
            self.y_data = list(df['sensor_d'])
        else:
            now = datetime.now()
            self.x_data = [now - timedelta(minutes=self.last_minutes) + timedelta(seconds=i) for i in
                           range(0, self.last_minutes * 60, 60)]
            self.y_data = [0 for _ in range(len(self.x_data))]

        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)
        self.ax.set_xlim(self.get_start_time(), self.get_start_time() + timedelta(minutes=self.last_minutes))

        if self.y_data:
            self.ax.set_ylim(min(self.y_data), max(self.y_data))
        else:
            self.ax.set_ylim(0, 1)

        self.canvas.draw_idle()  # redraw plot

    def run_update_loop(self):
        while True:
            self.update_graph()
            time.sleep(1)