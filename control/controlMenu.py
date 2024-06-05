import customtkinter as tk

class ControlMenu(tk.CTkFrame):  # Changed from CTkTabview to CTkFrame
    def __init__(self, master, height, width, controller):
        # Initialize the frame with a border
        super().__init__(master, height=height, width=width, border_width=2, corner_radius=0)
        self.controller = controller
        self.controller.start_engine_thread()

        # Create a CTkTabview inside this frame
        self.tabview = tk.CTkTabview(self, height=height-10, width=width-10)
        self.tabview.pack(padx=5, pady=5)

        self.tabview.add("Off")
        self.tabview.add("Manuel")
        self.tabview.add("Cycle")
        self.tabview.add("PID")
        self.tabview.add("Auto Tune")

        self.menu_off_frame = tk.CTkFrame(self.tabview.tab("Off"))
        self.menu_off_frame_button = tk.CTkButton(master=self.menu_off_frame, text="Turn OFF", command=self.controller.set_turn_off_flag)
        self.menu_off_frame_button.pack()
        self.menu_off_frame.pack()

        self.menu_manuel_frame = tk.CTkFrame(self.tabview.tab("Manuel"))
        self.menu_manuel_frame_button = tk.CTkButton(master=self.menu_manuel_frame, text="Turn On", command=self.set_manual_mode)
        self.menu_manuel_frame_button.pack()
        self.menu_manuel_frame_entry_setpoint = tk.CTkEntry(self.menu_manuel_frame, width=width-20)
        self.menu_manuel_frame_entry_setpoint.pack()
        self.menu_manuel_frame.pack()

    def set_manual_mode(self):
        temp_value = self.menu_manuel_frame_entry_setpoint.get()
        self.controller.set_manual_mode_flag(temp_value)
