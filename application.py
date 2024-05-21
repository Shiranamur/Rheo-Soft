import customtkinter as tk
from settings import AppSettings
from toolbox import ToolboxFrame
from timeline import TimelineCanvas
from graph import GraphFrame

class Application(tk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry(AppSettings.default_geometry(self))
        self.title(AppSettings.title)
        self.create_toolbox(20)
        self.create_timeline(20)
        self.create_graph(80, 80)

    def create_toolbox(self, width_percent):
        tb_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.toolbox = ToolboxFrame(self, width=tb_width)
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)

    def create_timeline(self,height_percent):
        tl_height = int(self.winfo_screenheight()) * (height_percent / 100)
        self.timeline = TimelineCanvas(self, height=tl_height)
        self.timeline.pack(side="bottom", fill="x", expand=False,)

    def create_graph(self, height_percent, width_percent):
        graph_height = int(self.winfo_screenheight()) * (height_percent / 100)
        graph_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.graph = GraphFrame(self, self.timeline.sequences_list, height=graph_height, width=graph_width)
        self.graph.pack(side="top")
