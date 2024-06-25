# tabview.py
import customtkinter as tk

from cycleEditor.toolbox import ToolboxFrame
from cycleEditor.timeline import TimelineCanvas
from cycleEditor.graph import GraphFrame

from control.pumpEngine import Pump
from control.controllerEngine import Controller
from control.controlMenu import ControlMenu
from control.controlMenu import AlarmMenu
from control.controlMenu import StatusMenu
from control.runtime_graph import GraphPage

class Tabview(tk.CTkTabview):
    def __init__(self, master, pump_port, controller_port):
        super().__init__(master)

        self.pump_port = pump_port
        self.controller_port = controller_port

        self.controller = Controller(self.controller_port)
        self.controller.connect_controller()
        print("controller initiated")

        self.pump = Pump(self.pump_port)
        self.pump.start_thread()
        print("pump initiated, and running")

        self.add("Contrôle en direct")
        self.add("Editeur de Cycle")

        """Create tab1 content"""
        self.create_control_menu(master=self.tab("Contrôle en direct"), width_percent=35, height_percent=20)
        self.create_alarm_menu(master=self.tab("Contrôle en direct"), width_percent=35, height_percent=20)
        self.create_status_menu(master=self.tab("Contrôle en direct"), width_percent=30, height_percent=20)
        self.create_runtime_graph(master=self.tab("Contrôle en direct"), width_percent=100, height_percent=70)

        """Create tab2 content"""
        self.create_toolbox(master=self.tab("Editeur de Cycle"), width_percent=20)
        self.create_timeline(master=self.tab("Editeur de Cycle"), height_percent=20)
        self.create_graph(master=self.tab("Editeur de Cycle"), height_percent=80, width_percent=80)

    def create_runtime_graph(self, master, width_percent, height_percent):
        self.update_idletasks()  # Ensure the size is updated
        rg_width = int(self.winfo_width() * (width_percent / 100))
        rg_height = int(self.winfo_height() * (height_percent / 100))
        print(f"Runtime graph dimensions: width={rg_width}, height={rg_height}")  # Debug statement
        self.graph_page = GraphPage(master, last_minutes=15, height=rg_height, width=rg_width)
        self.graph_page.grid(column=0, row=2, sticky="nsew", padx=10, pady=(0, 20))

    def create_control_menu(self, master, width_percent, height_percent):
        cm_width = int(self.winfo_screenwidth() * (width_percent / 100))
        cm_height = int(self.winfo_screenheight() * (height_percent / 100))
        print(f"Control menu dimensions: width={cm_width}, height={cm_height}")
        self.control_menu = ControlMenu(master, height=cm_height, width=cm_width, controller=self.controller)
        self.control_menu.pack(side="left", anchor="s", fill="x")

    def create_alarm_menu(self, master, width_percent, height_percent):
        am_width = int(self.winfo_screenwidth() * (width_percent / 100))
        am_height = int(self.winfo_screenheight() * (height_percent / 100))
        self.alarm_menu = AlarmMenu(master, height=am_height, width=am_width, controller=self.controller)
        self.alarm_menu.pack(side="left", anchor="s", fill="x", expand=True)

    def create_status_menu(self, master, width_percent, height_percent):
        sm_width = int(self.winfo_screenwidth() * (width_percent / 100))
        sm_height = int(self.winfo_screenheight() * (height_percent / 100))
        self.status_menu = StatusMenu(master, height=sm_height, width=sm_width, controller=self.controller,
                                      pump=self.pump)
        self.status_menu.pack(side="left", anchor="s", fill="x", expand=True)

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