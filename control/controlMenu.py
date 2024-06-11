import customtkinter as tk

class ControlMenu(tk.CTkFrame):
    def __init__(self, master, height, width, controller):
        super().__init__(master, height=height, width=width, border_width=2, corner_radius=0)
        self.controller = controller
        self.controller.start_engine_thread()

        self.tabview = tk.CTkTabview(self, height=height-10, width=width-10)
        self.tabview.pack(padx=5, pady=5)

        self.tabview.add("Off")
        self.tabview.add("Manuel")
        self.tabview.add("Cycle")
        self.tabview.add("PID")
        self.tabview.add("Auto Tune")

        # Start checking for tab changes
        self.previous_tab = self.tabview.get()
        self.check_tab_change()

        # Off tab
        self.menu_off_frame = tk.CTkFrame(self.tabview.tab("Off"))
        self.menu_off_frame_button = tk.CTkButton(master=self.menu_off_frame, text="Turn OFF", command=self.controller.set_turn_off_flag)
        self.menu_off_frame_button.pack()
        self.menu_off_frame_logging_checkbox = tk.CTkCheckBox(master=self.menu_off_frame, text="Log Data", command=self.toggle_logging)
        self.menu_off_frame_logging_checkbox.pack()
        self.menu_off_frame.pack()

        # Manuel tab
        self.menu_manuel_frame = tk.CTkFrame(self.tabview.tab("Manuel"))
        self.menu_manuel_frame_button = tk.CTkButton(master=self.menu_manuel_frame, text="Turn On", command=self.start_manual_mode)
        self.menu_manuel_frame_button.pack()
        self.menu_manuel_frame_entry_setpoint = tk.CTkEntry(self.menu_manuel_frame, width=width-20)
        self.menu_manuel_frame_entry_setpoint.pack()
        self.menu_manuel_frame_logging_checkbox = tk.CTkCheckBox(master=self.menu_manuel_frame, text="Log Data", command=self.toggle_logging)
        self.menu_manuel_frame_logging_checkbox.pack()
        self.menu_manuel_frame.pack()

        # PID tab
        self.menu_pid_frame = tk.CTkFrame(self.tabview.tab("PID"))
        self.menu_pid_frame_new_temp = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New Temp")
        self.menu_pid_frame_new_temp.pack()

        self.menu_pid_frame_current_p_gain = tk.CTkTextbox(self.menu_pid_frame, width=width-20, height=30)
        self.menu_pid_frame_current_p_gain.insert(tk.END, f"Current P Gain Value: {self.controller.r5_gain_value}")
        self.menu_pid_frame_current_p_gain.pack()

        self.menu_pid_frame_new_p_gain = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New P Gain Value")
        self.menu_pid_frame_new_p_gain.pack()

        self.menu_pid_frame_current_i_gain = tk.CTkTextbox(self.menu_pid_frame, width=width-20, height=30)
        self.menu_pid_frame_current_i_gain.insert(tk.END, f"Current I Gain Value: {self.controller.r6_gain_value}")
        self.menu_pid_frame_current_i_gain.pack()

        self.menu_pid_frame_new_i_gain = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New I Gain Value")
        self.menu_pid_frame_new_i_gain.pack()

        self.menu_pid_frame_current_d_gain = tk.CTkTextbox(self.menu_pid_frame, width=width-20, height=30)
        self.menu_pid_frame_current_d_gain.insert(tk.END, f"Current D Gain Value: {self.controller.r7_gain_value}")
        self.menu_pid_frame_current_d_gain.pack()

        self.menu_pid_frame_new_d_gain = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New D Gain Value")
        self.menu_pid_frame_new_d_gain.pack()

        self.menu_pid_frame_button = tk.CTkButton(master=self.menu_pid_frame, text="Start with current PID value", command=self.start_pid_mode)
        self.menu_pid_frame_button.pack()
        self.menu_pid_frame_logging_checkbox = tk.CTkCheckBox(master=self.menu_pid_frame, text="Log Data", command=self.toggle_logging)
        self.menu_pid_frame_logging_checkbox.pack()
        self.menu_pid_frame.pack()

        # Auto Tune tab
        self.menu_autotune_frame = tk.CTkFrame(self.tabview.tab("Auto Tune"))
        self.menu_autotune_frame_button = tk.CTkButton(master=self.menu_autotune_frame, text="Start Autotune", command=self.start_autotune)
        self.menu_autotune_frame_button.pack()
        self.menu_autotune_status_textbox = tk.CTkTextbox(master=self.menu_autotune_frame, width=width-20, height=100)
        self.menu_autotune_status_textbox.pack()
        self.menu_autotune_frame_logging_checkbox = tk.CTkCheckBox(master=self.menu_autotune_frame, text="Log Data", command=self.toggle_logging)
        self.menu_autotune_frame_logging_checkbox.pack()
        self.menu_autotune_frame.pack()

    def start_manual_mode(self):
        temp_value = self.menu_manuel_frame_entry_setpoint.get()
        self.controller.set_manual_mode_flag(temp_value)

    def start_pid_mode(self):
        new_temp = self.menu_pid_frame_new_temp.get()
        new_p_gain = self.menu_pid_frame_new_p_gain.get()
        new_i_gain = self.menu_pid_frame_new_i_gain.get()
        new_d_gain = self.menu_pid_frame_new_d_gain.get()
        self.controller.set_pid_flag(new_temp, new_p_gain, new_i_gain, new_d_gain)

    def start_autotune(self):
        self.controller.set_start_autotune_flag()

    def update_autotune_status(self, message):
        self.menu_autotune_status_textbox.delete("1.0", tk.END)
        self.menu_autotune_status_textbox.insert(tk.END, message)

    def on_tab_change(self):
        selected_tab = self.tabview.get()  # Get the name of the selected tab
        if selected_tab == "PID":
            self.controller.read_pid_values = True

    def toggle_logging(self):
        self.controller.set_logging()

    def check_tab_change(self):
        current_tab = self.tabview.get()
        if current_tab != self.previous_tab:
            self.on_tab_change()
            self.previous_tab = current_tab
        self.after(100, self.check_tab_change)  # Check every 100ms
