import customtkinter as tk

from cycleEditor.toolbox import ToolboxFrame
from cycleEditor.timeline import TimelineCanvas
from cycleEditor.graph import GraphFrame


class Tabview(tk.CTkTabview):
    def __init__(self, master):
        super().__init__(master)

        self.add("Contrôle en direct")
        self.add("Editeur de Cycle")

        self.create_toolbox(master=self.tab("Editeur de Cycle"), width_percent=20)
        self.create_timeline(master=self.tab("Editeur de Cycle"), height_percent=20)
        self.create_graph(master=self.tab("Editeur de Cycle"), height_percent=80, width_percent=80)

    def create_toolbox(self, master, width_percent):
        tb_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.toolbox = ToolboxFrame(master, width=tb_width)
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)

    def create_timeline(self, master, height_percent):
        tl_height = int(self.winfo_screenheight()) * (height_percent / 100)
        self.timeline = TimelineCanvas(master, height=tl_height)
        self.timeline.pack(side="bottom", fill="x", expand=False)

    def create_graph(self, master, height_percent, width_percent):
        graph_height = int(self.winfo_screenheight()) * (height_percent / 100)
        graph_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.graph = GraphFrame(master, self.timeline.sequences_list, height=graph_height, width=graph_width)
        self.graph.pack(side="top")
