import customtkinter as tk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from threading import Lock
import redis


class GraphPage(tk.CTkFrame):

    def __init__(self, master, height, last_minutes=15):
        super().__init__(master, height=height)
        self.last_minutes = last_minutes
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)

        self.x_data, self.y_data = self.get_initial_data()
        self.plot = self.ax.plot(self.x_data, self.y_data, label='Sensor D')[0]
        self.ax.set_ylim(0, 100)  # Adjust according to your sensor data range
        self.ax.set_xlim(datetime.now() - timedelta(minutes=self.last_minutes), datetime.now())

        self.ax.grid(which='major', axis='both', linestyle='--', color='grey', alpha=0.5)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.scale = tk.CTkSlider(self, from_=15, to=180, orientation="horizontal", command=self.update_minutes)
        self.scale.set(self.last_minutes)
        self.scale.pack(side=tk.BOTTOM, fill="x", expand=False)

        self.animate()  # launch the animation

    @staticmethod
    def fetch_data_from_redis(last_minutes=15):
        with Lock():
            try:
                r = redis.Redis(host='localhost', port=6379, db=0)
                keys = r.keys('data_*')
                data_list = []
                for key in keys:
                    if r.type(key) == b'hash':  # Ensure the key is of hash type
                        data = r.hgetall(key)
                        timestamp = datetime.strptime(data[b'timestamp'].decode('utf-8'), "%Y-%m-%d %H:%M:%S")
                        if timestamp >= datetime.now() - timedelta(minutes=last_minutes):
                            sensor_d = float(data[b'sensor_d'].decode('utf-8'))
                            sensor_a = float(data[b'sensor_a'].decode('utf-8'))
                            data_list.append((timestamp, sensor_d, sensor_a))
                df = pd.DataFrame(data_list, columns=['timestamp', 'sensor_d', 'sensor_a'])
                df.sort_values('timestamp', inplace=True)
                return df
            except Exception as e:
                print(f"Error fetching data: {e}")
                return pd.DataFrame(columns=['timestamp', 'sensor_d', 'sensor_a'])

    def get_initial_data(self):
        df = self.fetch_data_from_redis(self.last_minutes)
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

    def update_graph(self):
        df = self.fetch_data_from_redis(self.last_minutes)
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
        self.ax.set_xlim(datetime.now() - timedelta(minutes=self.last_minutes), datetime.now())

        if self.y_data:
            self.ax.set_ylim(min(self.y_data), max(self.y_data))
        else:
            self.ax.set_ylim(0, 1)

        self.canvas.draw_idle()  # redraw plot

    def animate(self):
        self.update_graph()
        self.after(1000, self.animate)  # repeat after 1s

# class App(tk.CTk):
#      def __init__(self):
#         super().__init__()
# # #
#         self.geometry('800x600')
#         self.title('CustomTkinter TabView Example')
# # #
#         self.tab_view = tk.CTkTabview(self)
#         self.tab_view.pack(fill='both', expand=True)
# #
#         # Add tab to the tab view
#         self.tab_view.add("Graph Page")
#
#         # Get the frame of the tab and create GraphPage within it
#         graph_tab = self.tab_view.tab("Graph Page")
#         self.graph_page = GraphPage(graph_tab, last_minutes=15)
#         self.graph_page.pack(fill='both', expand=True)
#         print("GraphPage initialized with master:", self.graph_page.master)
# #
# #
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()
