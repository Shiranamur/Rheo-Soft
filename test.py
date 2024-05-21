import customtkinter as ctk
from settings import AppSettings
from toolbox import ToolboxFrame
from timeline import TimelineCanvas
from graph import GraphFrame

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(AppSettings.title)
        self.geometry(AppSettings.default_geometry(self))

        # Create a tab view
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=1, fill="both")

        # Add tabs
        self.tabview.add("Part 1")
        self.tabview.add("Part 2")

        # Track loaded tabs
        self.loaded_tabs = {"Part 1": False, "Part 2": False}

        # Load Part 1 initially
        self.load_part1(self.tabview.tab("Part 1"))

        # Create an option menu to switch tabs
        self.option_menu = ctk.CTkOptionMenu(self, values=["Part 1", "Part 2"], command=self.switch_tab)
        self.option_menu.pack(pady=20)

    def load_part1(self, tab):
        label = ctk.CTkLabel(tab, text="This is Part 1")
        label.pack(pady=20)
        self.loaded_tabs["Part 1"] = True

    def load_part2(self, tab):
        self.create_toolbox(tab, 20)
        self.create_timeline(tab, 20)
        self.create_graph(tab, 80, 80)
        self.loaded_tabs["Part 2"] = True

    def check_tab(self):
        selected_tab = self.tabview.get()  # Get the currently selected tab
        if selected_tab == "Part 2" and not self.loaded_tabs["Part 2"]:
            self.load_part2(self.tabview.tab("Part 2"))

    def switch_tab(self, tab_name):
        self.tabview.set(tab_name)  # Set the selected tab
        self.check_tab()

    def create_toolbox(self, tab, width_percent):
        tb_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.toolbox = ToolboxFrame(tab, width=tb_width)
        self.toolbox.pack(side="left", fill="y", expand=False)
        self.toolbox.pack_propagate(False)

    def create_timeline(self, tab, height_percent):
        tl_height = int(self.winfo_screenheight()) * (height_percent / 100)
        self.timeline = TimelineCanvas(tab, height=tl_height)
        self.timeline.pack(side="bottom", fill="x", expand=False)

    def create_graph(self, tab, height_percent, width_percent):
        graph_height = int(self.winfo_screenheight()) * (height_percent / 100)
        graph_width = int(self.winfo_screenwidth()) * (width_percent / 100)
        self.graph = GraphFrame(tab, self.timeline.sequences_list, height=graph_height, width=graph_width)
        self.graph.pack(side="top")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
