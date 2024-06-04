import customtkinter as tk


class ControlMenu(tk.CTkTabview):
    def __init__(self, master, height, width, controller):
        super().__init__(master, height=height, width=width)
        self.controller = controller
        self.controller.start_cycle_thread()

        self.add("Off")
        self.add("Manuel")
        self.add("Cycle")
        self.add("PID")
        self.add("Auto Tune")

        self.menu_off_frame = tk.CTkFrame(master)
        self.menu_off_frame_button = tk.CTkButton(master=self.menu_off_frame, text="Turn OFF", command=self.controller.send_off_command())


        self.menu_manuel_frame = tk.CTkFrame(master)
        self.menu_manuel_frame_button = tk.CTkButton(master=self.menu_manuel_frame, text="Turn On", command=self.controller.send_manuel_command())