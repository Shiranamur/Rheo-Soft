import tkinter as tk
from settings import AppSettings
from toolbox import ToolboxFrame


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry(AppSettings.default_geometry(self))
        self.title(AppSettings.title)
        self.create_toolbox(20)
        self.create_timeline()
        self.create_graph()

    def create_toolbox(self, width_percent):
        tb_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.toolbox = ToolboxFrame(self, width=int(tb_width))
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)

    def create_timeline(self):
        pass

    def create_graph(self):
        pass
