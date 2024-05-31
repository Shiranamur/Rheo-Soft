# controlGraph.py
import customtkinter as tk
from control.coms import Controller

class controlGraphFrame(tk.CTkFrame):
    def __init__(self, master, height, width, port):
        super().__init__(master, height=height, width=width)

        self.controller_port = port
        self.controller = Controller(self.controller_port)
        self.controller.connect()

        self.controller.start_r68_thread()
        self.controller.start_r65_thread()

        self.r68_label = tk.CTkLabel(self, text='')
        self.r68_label.pack(pady=20)

        self.r65_label = tk.CTkLabel(self, text='')
        self.r65_label.pack(pady=20)

        self.update_r68_data()
        self.update_r65_data()

    def update_r68_data(self):
        d_sensor_data = self.controller.r68_output()
        if d_sensor_data:
            self.r68_label.configure(text='sensor d:' + d_sensor_data)
        self.after(500, self.update_r68_data)  # Schedule next update

    def update_r65_data(self):
        a_sensor_data = self.controller.r65_output()
        if a_sensor_data:
            self.r65_label.configure(text='sensor a:' + a_sensor_data)
        self.after(500, self.update_r65_data)  # Schedule next update
