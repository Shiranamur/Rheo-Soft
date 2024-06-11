import customtkinter as tk
from toolbox import ToolboxFrame
from timeline import TimelineCanvas
from graph import GraphFrame


class CycleEditorApp(tk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cycle Editor Test")
        self.geometry("1200x800")

        self.create_toolbox()
        self.create_timeline()
        self.create_graph()

    def create_toolbox(self):
        """Creates the ToolboxFrame"""
        tb_width = int(self.winfo_screenwidth() * 0.15)
        self.toolbox = ToolboxFrame(self, width=tb_width)
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)

    def create_timeline(self):
        """Creates the TimelineCanvas"""
        tl_height = int(self.winfo_screenheight() * 0.2)
        self.timeline = TimelineCanvas(self, height=tl_height)
        self.timeline.pack(side="bottom", fill="x", expand=False)

    def create_graph(self):
        """Creates the GraphFrame"""
        graph_height = int(self.winfo_screenheight() * 0.8)
        graph_width = int(self.winfo_screenwidth() * 0.8)
        self.graph = GraphFrame(self, self.timeline.sequences_list, height=graph_height, width=graph_width)
        self.graph.pack(side="top", fill="both", expand=True)


if __name__ == "__main__":
    app = CycleEditorApp()
    app.mainloop()
