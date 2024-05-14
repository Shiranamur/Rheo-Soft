import tkinter as tk
from settings import AppSettings
from toolbox import ToolboxFrame
from timelinetest import TimelineCanvas


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry(AppSettings.default_geometry(self))
        self.title(AppSettings.title)
        self.create_toolbox(20)
        self.create_timeline(20)
        self.create_graph()

    def create_toolbox(self, width_percent):
        tb_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.toolbox = ToolboxFrame(self, width=int(tb_width))
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)

    def create_timeline(self,height_percent):
        tl_height = int(self.winfo_screenheight()) * (height_percent / 100)
        self.timeline = TimelineCanvas(self, height=int(tl_height))
        self.timeline.pack(side="bottom", fill="x", expand=False,)

    def create_graph(self):
        pass
