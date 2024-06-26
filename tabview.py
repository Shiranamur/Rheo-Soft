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
        self.master = master

        self.pump_port = pump_port
        self.controller_port = controller_port

        self.controller = Controller(self.controller_port)
        self.controller.connect_controller()

        self.pump = Pump(self.pump_port)
        self.pump.start_thread()

        self.add("Contrôle en direct")
        self.add("Editeur de Cycle")

        """Create tab1 content"""
        self.create_menus_frame(master=self.tab("Contrôle en direct"))
        self.create_live_graph(master=self.tab("Contrôle en direct"), height_percent=70)

        """Create tab2 content"""
        self.create_toolbox(master=self.tab("Editeur de Cycle"), width_percent=20)
        self.create_timeline(master=self.tab("Editeur de Cycle"), height_percent=20)
        self.create_graph(master=self.tab("Editeur de Cycle"), height_percent=80, width_percent=80)

    def create_live_graph(self, master, height_percent):
        lg_height = int(self.winfo_screenheight() * (height_percent/100))
        self.graph_page = GraphPage(master, last_minutes=15, height=lg_height)
        self.graph_page.pack(fill=tk.X, expand=True, side=tk.TOP)
        self.graph_page.propagate(False)

    def create_menus_frame(self, master):
        """Create a frame to encapsulate the control menu, alarm menu, and status menu"""
        menus_frame = tk.CTkFrame(master)
        menus_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_control_menu(menus_frame, row=0, column=0)
        self.create_alarm_menu(menus_frame, row=0, column=1)
        self.create_status_menu(menus_frame, row=0, column=2)

    def create_control_menu(self, master, row, column):
        cm_width = int(self.winfo_screenwidth() * (35 / 100))
        cm_height = int(self.winfo_screenheight() * (20 / 100))
        self.control_menu = ControlMenu(master, height=cm_height, width=cm_width, controller=self.controller)
        self.control_menu.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

    def create_alarm_menu(self, master, row, column):
        am_width = int(self.winfo_screenwidth() * (35 / 100))
        am_height = int(self.winfo_screenheight() * (20 / 100))
        self.alarm_menu = AlarmMenu(master, height=am_height, width=am_width, controller=self.controller)
        self.alarm_menu.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

    def create_status_menu(self, master, row, column):
        sm_width = int(self.winfo_screenwidth() * (30 / 100))
        sm_height = int(self.winfo_screenheight() * (20 / 100))
        self.status_menu = StatusMenu(master, height=sm_height, width=sm_width, controller=self.controller,
                                      pump=self.pump)
        self.status_menu.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

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
