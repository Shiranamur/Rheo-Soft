import tkinter as tk
import sqlite3
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import matplotlib.dates as mdates


def fetch_data(last_minutes=15):
    try:
        conn = sqlite3.connect('database.db')
        query = '''
        SELECT timestamp, sensorD, sensorA
        FROM sensor_data
        WHERE timestamp >= datetime('now', '-{} minutes')
        ORDER BY timestamp ASC
        '''.format(last_minutes)
        df = pd.read_sql_query(query, conn)
        conn.close()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame(columns=['timestamp', 'sensorD', 'sensorA'])


class GraphPage(tk.Frame):

    def __init__(self, parent, last_minutes=15):
        tk.Frame.__init__(self, parent)
        self.last_minutes = last_minutes
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)

        self.x_data, self.y_data = self.get_initial_data()
        self.plot = self.ax.plot(self.x_data, self.y_data, label='Sensor D')[0]
        self.ax.set_ylim(0, 100)  # Adjust according to your sensor data range
        self.ax.set_xlim(datetime.now() - timedelta(minutes=self.last_minutes), datetime.now())

        label = tk.Label(self, text="Live Sensor Data Plotting")
        label.pack(pady=10, padx=10)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def get_initial_data(self):
        df = fetch_data(self.last_minutes)
        if not df.empty:
            return list(df['timestamp']), list(df['sensorD'])
        else:
            now = datetime.now()
            x_data = [now - timedelta(minutes=self.last_minutes) + timedelta(seconds=i) for i in
                      range(0, self.last_minutes * 60, 60)]
            y_data = [0 for _ in range(len(x_data))]
            return x_data, y_data

    def animate(self):
        df = fetch_data(self.last_minutes)
        if not df.empty:
            self.x_data = list(df['timestamp'])
            self.y_data = list(df['sensorD'])
        else:
            now = datetime.now()
            self.x_data = [now - timedelta(minutes=self.last_minutes) + timedelta(seconds=i) for i in
                           range(0, self.last_minutes * 60, 60)]
            self.y_data = [0 for _ in range(len(self.x_data))]

        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)
        self.ax.set_xlim(datetime.now() - timedelta(minutes=self.last_minutes), datetime.now())
        self.ax.set_ylim(min(self.y_data), max(self.y_data))
        self.canvas.draw_idle()  # redraw plot
        self.after(1000, self.animate)  # repeat after 1s


root = tk.Tk()
graph = GraphPage(root, last_minutes=15)
graph.pack(fill='both', expand=True)
root.geometry('500x400')
graph.animate()  # launch the animation
root.mainloop()
