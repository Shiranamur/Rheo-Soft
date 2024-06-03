# tabview.py
import customtkinter as tk

from cycleEditor.toolbox import ToolboxFrame
from cycleEditor.timeline import TimelineCanvas
from cycleEditor.graph import GraphFrame

from control.pumpFrame import PumpFrame
from control.controlGraph import ControlGraphFrame
from control.coms import Controller

class Tabview(tk.CTkTabview):
    def __init__(self, master, pump_port, controller_port):
        super().__init__(master)

        self.pump_port = pump_port
        self.controller_port = controller_port

        # Initialize the Controller instance
        self.controller = Controller(self.controller_port)

        self.add("Contrôle en direct")
        self.add("Editeur de Cycle")

        """Create tab1 content"""
        self.create_pump_output(master=self.tab("Contrôle en direct"), width_percent=10, height_percent=5)
        self.create_control_graph(master=self.tab("Contrôle en direct"), width_percent=10, height_percent=5)
        self.create_start_cycle_button(master=self.tab("Contrôle en direct"))

        """Create tab2 content"""
        self.create_toolbox(master=self.tab("Editeur de Cycle"), width_percent=20)
        self.create_timeline(master=self.tab("Editeur de Cycle"), height_percent=20)
        self.create_graph(master=self.tab("Editeur de Cycle"), height_percent=80, width_percent=80)

    def create_start_cycle_button(self, master):
        self.start_cycle_button = tk.CTkButton(master, text="Launch Cycle", command=self.controller.start_cycle_thread)
        self.start_cycle_button.pack(side=tk.LEFT)

    def create_pump_output(self, master, width_percent, height_percent):
        """Creates the pump output frame"""
        po_width = int(self.winfo_screenwidth() * (width_percent / 100))
        po_height = int(self.winfo_screenheight() * (height_percent / 100))
        self.pump_data = PumpFrame(master, height=po_height, width=po_width, port=self.pump_port)
        self.pump_data.pack(side=tk.TOP, expand=False, anchor="w")

    def create_control_graph(self, master, width_percent, height_percent):
        cg_width = int(self.winfo_screenwidth() * (width_percent / 100))
        cg_height = int(self.winfo_screenheight() * (height_percent / 100))
        self.control_graph = ControlGraphFrame(master, height=cg_height, width=cg_width, port=self.controller_port)
        self.control_graph.pack(side=tk.TOP, expand=False, anchor="e")

    def create_toolbox(self, master, width_percent):
        """Creates the ToolboxFrame in second tab"""
        tb_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.toolbox = ToolboxFrame(master, width=tb_width)
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)

    def create_timeline(self, master, height_percent):
        """Creates the timeline canvas in second tab"""
        tl_height = int(self.winfo_screenheight()) * (height_percent / 100)
        self.timeline = TimelineCanvas(master, height=tl_height)
        self.timeline.pack(side="bottom", fill="x", expand=False)

    def create_graph(self, master, height_percent, width_percent):
        """Creates the graph frame in second tab"""
        graph_height = int(self.winfo_screenheight()) * (height_percent / 100)
        graph_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.graph = GraphFrame(master, self.timeline.sequences_list, height=graph_height, width=graph_width)
        self.graph.pack(side="top")
