# tabview.py
import customtkinter as tk

from cycleEditor.toolbox import ToolboxFrame
from cycleEditor.timeline import TimelineCanvas
from cycleEditor.graph import GraphFrame

from control.pumpFrame import PumpFrame
from control.controllerEngine import Controller
from control.controlMenu import ControlMenu


class Tabview(tk.CTkTabview):
    def __init__(self, master, pump_port, controller_port):
        super().__init__(master)

        self.pump_port = pump_port
        self.controller_port = controller_port

        print("Initialize the Controller instance")
        self.controller = Controller(self.controller_port)
        print("Controller initialized:", self.controller, " ;connecting")
        self.controller.connect()
        print("Controller connected")

        self.add("Contrôle en direct")
        self.add("Editeur de Cycle")

        """Create tab1 content"""
        print("Creating tab1 content")
        self.create_pump_output(master=self.tab("Contrôle en direct"), width_percent=10, height_percent=5)
        print("Pump output created")
        # self.create_control_graph(master=self.tab("Contrôle en direct"), width_percent=10, height_percent=5)
        print("Control graph created")
        # self.create_start_cycle_button(master=self.tab("Contrôle en direct"))

        self.add_control_menu(master=self.tab("Contrôle en direct"), width_percent=20, height_percent=20)
        print("Control menu added")

        """Create tab2 content"""
        print("Creating tab2 content")
        self.create_toolbox(master=self.tab("Editeur de Cycle"), width_percent=20)
        print("Toolbox created")
        self.create_timeline(master=self.tab("Editeur de Cycle"), height_percent=20)
        print("Timeline created")
        self.create_graph(master=self.tab("Editeur de Cycle"), height_percent=80, width_percent=80)
        print("Graph created")

    def add_control_menu(self, master, width_percent, height_percent):
        print("Adding control menu with width_percent:", width_percent, "height_percent:", height_percent)
        cm_width = int(self.winfo_screenwidth() * (width_percent / 100))
        cm_height = int(self.winfo_screenheight() * (height_percent / 100))
        print("Control menu dimensions:", cm_width, cm_height)
        self.create_control_menu = ControlMenu(master, height=cm_height, width=cm_width, controller=self.controller)
        self.create_control_menu.pack(side=tk.LEFT)
        print("Control menu packed")

    def create_pump_output(self, master, width_percent, height_percent):
        """Creates the pump output frame"""
        print("Creating pump output with width_percent:", width_percent, "height_percent:", height_percent)
        po_width = int(self.winfo_screenwidth() * (width_percent / 100))
        po_height = int(self.winfo_screenheight() * (height_percent / 100))
        print("Pump output dimensions:", po_width, po_height)
        self.pump_data = PumpFrame(master, height=po_height, width=po_width, port=self.pump_port)
        self.pump_data.pack(side=tk.TOP, expand=False, anchor="w")
        print("Pump output packed")

    # def create_control_graph(self, master, width_percent, height_percent):
    #     print("Creating control graph with width_percent:", width_percent, "height_percent:", height_percent)
    #     cg_width = int(self.winfo_screenwidth() * (width_percent / 100))
    #     cg_height = int(self.winfo_screenheight() * (height_percent / 100))
    #     print("Control graph dimensions:", cg_width, cg_height)
    #     self.control_graph = ControlGraphFrame(master, height=cg_height, width=cg_width, port=self.controller_port)
    #     self.control_graph.pack(side=tk.TOP, expand=False, anchor="e")
    #     print("Control graph packed")

    def create_toolbox(self, master, width_percent):
        """Creates the ToolboxFrame in second tab"""
        print("Creating toolbox with width_percent:", width_percent)
        tb_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        print("Toolbox dimensions:", tb_width)
        self.toolbox = ToolboxFrame(master, width=tb_width)
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)
        print("Toolbox packed")

    def create_timeline(self, master , height_percent):
        """Creates the timeline canvas in second tab"""
        print("Creating timeline with height_percent:", height_percent)
        tl_height = int(self.winfo_screenheight()) * (height_percent / 100)
        print("Timeline dimensions:", tl_height)
        self.timeline = TimelineCanvas(master, height=tl_height)
        self.timeline.pack(side="bottom", fill="x", expand=False)
        print("Timeline packed")

    def create_graph(self, master, height_percent, width_percent):
        """Creates the graph frame in second tab"""
        print("Creating graph with height_percent:", height_percent, "width_percent:", width_percent)
        graph_height = int(self.winfo_screenheight()) * (height_percent / 100)
        graph_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        print("Graph dimensions:", graph_width, graph_height)
        self.graph = GraphFrame(master, self.timeline.sequences_list, height=graph_height, width=graph_width)
        self.graph.pack(side="top")
        print("Graph packed")
