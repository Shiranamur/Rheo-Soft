import customtkinter as tk
from tkinter import messagebox


class ControlMenu(tk.CTkFrame):
    def __init__(self, master, height, width, controller):
        super().__init__(master, height=height, width=width, border_width=2)
        self.controller = controller
        self.controller.start_engine_thread()

        self.tabview = tk.CTkTabview(self, height=height - 10, width=width - 10)
        self.tabview.pack(padx=5, pady=5)

        self.tabview.add("Cycle")
        self.tabview.add("PID")
        self.tabview.add("Auto Tune")

        # Start checking for tab changes
        self.previous_tab = self.tabview.get()
        self.check_tab_change()

        # PID tab
        self.menu_pid_frame = tk.CTkFrame(self.tabview.tab("PID"))
        self.menu_pid_frame_new_temp = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New Temp")
        self.menu_pid_frame_new_temp.pack()

        self.menu_pid_frame_current_p_gain = tk.CTkLabel(self.menu_pid_frame, width=width - 20, height=30,
                                                         text=f"Current P Gain Value: {self.controller.r5_gain_value}")
        self.menu_pid_frame_current_p_gain.pack()

        self.menu_pid_frame_new_p_gain = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New P Gain Value")
        self.menu_pid_frame_new_p_gain.pack()

        self.menu_pid_frame_current_i_gain = tk.CTkLabel(self.menu_pid_frame, width=width - 20, height=30,
                                                         text=f"Current I Gain Value: {self.controller.r6_gain_value}")
        self.menu_pid_frame_current_i_gain.pack()

        self.menu_pid_frame_new_i_gain = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New I Gain Value")
        self.menu_pid_frame_new_i_gain.pack()

        self.menu_pid_frame_current_d_gain = tk.CTkLabel(self.menu_pid_frame, width=width - 20, height=30,
                                                         text=f"Current D Gain Value: {self.controller.r7_gain_value}")
        self.menu_pid_frame_current_d_gain.pack()

        self.menu_pid_frame_new_d_gain = tk.CTkEntry(self.menu_pid_frame, placeholder_text="New D Gain Value")
        self.menu_pid_frame_new_d_gain.pack()

        self.menu_pid_frame_button = tk.CTkButton(master=self.menu_pid_frame, text="Start with current PID value",
                                                  command=self.start_pid_mode)
        self.menu_pid_frame_button.pack()
        self.menu_pid_frame.pack()

        # Auto Tune tab
        self.menu_autotune_frame = tk.CTkFrame(self.tabview.tab("Auto Tune"))
        self.menu_autotune_frame_button = tk.CTkButton(master=self.menu_autotune_frame, text="Start Autotune",
                                                       command=self.start_autotune)
        self.menu_autotune_frame_button.pack()
        self.menu_autotune_status_label = tk.CTkLabel(master=self.menu_autotune_frame, width=width - 20, height=100,
                                                      text="")
        self.menu_autotune_status_label.pack()
        self.menu_autotune_frame.pack()

        # Cycle tab
        self.menu_cycle_frame = tk.CTkFrame(self.tabview.tab("Cycle"))

        self.high_temp_entry = tk.CTkEntry(self.menu_cycle_frame, placeholder_text="Set high temperature point")
        self.high_temp_entry.pack(pady=2)

        self.low_temp_entry = tk.CTkEntry(self.menu_cycle_frame, placeholder_text="Set low temperature point")
        self.low_temp_entry.pack(pady=2)

        self.time_btw_switchover_entry = tk.CTkEntry(self.menu_cycle_frame,
                                                     placeholder_text="Set time between switchover once temp is reached")
        self.time_btw_switchover_entry.pack(pady=2)

        self.wanted_nb_cycle_entry = tk.CTkEntry(self.menu_cycle_frame, placeholder_text="Set wanted number of cycles")
        self.wanted_nb_cycle_entry.pack(pady=2)

        self.percentage_checkbox = tk.CTkCheckBox(self.menu_cycle_frame, text="Use round up %")
        self.percentage_checkbox.pack(pady=2)

        self.percentage_entry = tk.CTkEntry(self.menu_cycle_frame,
                                            placeholder_text="Percentage Threshold of temp for switching point")
        self.percentage_entry.pack(pady=2)

        self.cycle_number_label = tk.CTkLabel(self.menu_cycle_frame, text="")
        self.cycle_number_label.pack(pady=2)

        self.start_cycle_button = tk.CTkButton(self.menu_cycle_frame, text="Start Cycle", command=self.start_cycle_mode)
        self.start_cycle_button.pack(pady=2)

        self.menu_cycle_frame.pack()

    # Adding debug prints to start_cycle_mode in ControlMenu
    def start_cycle_mode(self):
        try:
            high_temp = float(self.high_temp_entry.get())
            low_temp = float(self.low_temp_entry.get())
            use_percentage = self.percentage_checkbox.get()
            percentage_threshold = int(self.percentage_entry.get()) if use_percentage else 0
            time_btw_switchover = float(self.time_btw_switchover_entry.get())
            cycle_nb = int(self.wanted_nb_cycle_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "All fields must be filled out correctly with valid values.")
            return

        if not high_temp or not low_temp or not time_btw_switchover or not cycle_nb:
            messagebox.showerror("Input Error", "All fields must be filled out correctly.")
        else:
            print(
                f"Starting cycle mode with high_temp: {high_temp}, low_temp: {low_temp}, use_percentage: {use_percentage}, "
                f"percentage_threshold: {percentage_threshold}, time_btw_switchover: {time_btw_switchover}, cycle_nb: {cycle_nb}")
            self.controller.set_cycle_mode_flag(high_temp, low_temp, use_percentage, percentage_threshold,
                                                time_btw_switchover, cycle_nb)

    def start_pid_mode(self):
        new_temp = self.menu_pid_frame_new_temp.get()
        new_p_gain = self.menu_pid_frame_new_p_gain.get()
        new_i_gain = self.menu_pid_frame_new_i_gain.get()
        new_d_gain = self.menu_pid_frame_new_d_gain.get()
        self.controller.set_pid_flag(new_temp, new_p_gain, new_i_gain, new_d_gain)

        # Reset the entry boxes
        self.menu_pid_frame_new_temp.delete(0, tk.END)
        self.menu_pid_frame_new_p_gain.delete(0, tk.END)
        self.menu_pid_frame_new_i_gain.delete(0, tk.END)
        self.menu_pid_frame_new_d_gain.delete(0, tk.END)

        self.after(500, self.update_pid_labels)

    def start_autotune(self):
        self.controller.set_start_autotune_flag()

    def update_autotune_status(self, message):
        self.menu_autotune_status_label.configure(text=message)

    def refresh_cycle_status(self):
        if self.tabview.get() == "Cycle":
            self.cycle_number_label.configure(text=self.controller.status_callback_cycle)
        self.after(5000, self.refresh_cycle_status)

    def refresh_autotune_status(self):
        if self.tabview.get() == "Auto Tune":
            if self.controller.status_callback:
                self.menu_autotune_status_label.configure(text=self.controller.status_callback)
            self.after(1000, self.refresh_autotune_status)  # Refresh every 1 second

    def on_tab_change(self):
        selected_tab = self.tabview.get()  # Get the name of the selected tab
        if selected_tab == "PID":
            self.controller.set_read_pid_values()
            self.after(500, self.update_pid_labels())
        if selected_tab == "Auto Tune":
            self.refresh_autotune_status()  # Start refreshing the status only when on the Auto Tune tab

    # Update labels after a delay to ensure values are read


    def check_tab_change(self):
        current_tab = self.tabview.get()
        if current_tab != self.previous_tab:
            self.on_tab_change()
            self.previous_tab = current_tab
        self.after(100, self.check_tab_change)  # Check every 100ms

    def update_pid_labels(self):
        self.menu_pid_frame_current_p_gain.configure(text=f"Current P Gain Value: {self.controller.r5_gain_value}")
        self.menu_pid_frame_current_i_gain.configure(text=f"Current I Gain Value: {self.controller.r6_gain_value}")
        self.menu_pid_frame_current_d_gain.configure(text=f"Current D Gain Value: {self.controller.r7_gain_value}")


class AlarmMenu(tk.CTkFrame):
    def __init__(self, master, height, width, controller):
        super().__init__(master, height=height, width=width, border_width=2)
        self.controller = controller

        self.tabview = tk.CTkTabview(self, height=height - 10, width=width - 10)
        self.tabview.pack(padx=5, pady=5)

        self.tabview.add("Alarm Temps")
        self.tabview.add("Alarm Enable")

        self.temp_frame = tk.CTkFrame(self.tabview.tab("Alarm Temps"), height=height - 10, width=width - 10)
        self.temp_frame.pack(padx=5, pady=5)

        self.sensor_d_hightemp_entry = tk.CTkEntry(self.temp_frame, placeholder_text="Sensor D High temperature alarm temp")
        self.sensor_d_hightemp_entry.pack(padx=5, pady=5)

        self.sensor_d_lowtemp_entry = tk.CTkEntry(self.temp_frame, placeholder_text="Sensor D Low temperature alarm temp")
        self.sensor_d_lowtemp_entry.pack(padx=5, pady=5)

        self.sensor_a_hightemp_entry = tk.CTkEntry(self.temp_frame, placeholder_text="Sensor A High temperature alarm temp")
        self.sensor_a_hightemp_entry.pack(padx=5, pady=5)

        self.sensor_a_lowtemp_entry = tk.CTkEntry(self.temp_frame, placeholder_text="Sensor A Low temperature alarm temp")
        self.sensor_a_lowtemp_entry.pack(padx=5, pady=5)

        self.alarm_button = tk.CTkButton(master=self.temp_frame, text="Send new alarm values", command=self.set_and_send_alarm_temps)
        self.alarm_button.pack(padx=5, pady=5)

    def set_and_send_alarm_temps(self):
        sdht = self.sensor_d_hightemp_entry.get()
        sdlt = self.sensor_d_lowtemp_entry.get()
        saht = self.sensor_a_hightemp_entry.get()
        salt = self.sensor_a_lowtemp_entry.get()
        self.controller.set_alarm_temps(sdht, sdlt, saht, salt)


class StatusMenu(tk.CTkFrame):
    def __init__(self, master, height, width, controller, pump):
        super().__init__(master, height=height, width=width, border_width=2)
        self.controller = controller
        self.pump = pump

        self.tabview = tk.CTkTabview(self, height=height - 10, width=width - 10)
        self.tabview.pack(padx=5, pady=5)
        self.tabview.add("Status Tab")

        # Off button frame taking 60% of the master size
        self.off_button_frame = tk.CTkFrame(self.tabview.tab("Status Tab"), height=int((height - 10) * 0.5), width=width - 10)
        self.off_button_frame.pack_propagate(False)
        self.off_button_frame.pack(fill="both", expand=True)

        # Turn OFF button big, red, filling its frame
        self.off_button = tk.CTkButton(master=self.off_button_frame, text="Turn OFF",
                                       command=self.controller.set_turn_off_flag,
                                       fg_color="red",
                                       text_color="white",
                                       height=int((height - 10) * 0.45), width=width - 10)
        self.off_button.pack(fill="both", expand=True, padx=25, pady=35)
        self.off_button.configure(font=("Helvetica", 20))

        # Controller and pump status frames each taking 30% of the available height
        self.controller_status_frame = tk.CTkFrame(self.tabview.tab("Status Tab"), height=int((height - 10) * 0.3), width=(width - 20) // 2)
        self.controller_status_frame.pack_propagate(False)
        self.controller_status_frame.pack(side=tk.LEFT, fill="both", expand=True)

        self.pump_status_frame = tk.CTkFrame(self.tabview.tab("Status Tab"), height=int((height - 10) * 0.3), width=(width - 20) // 2)
        self.pump_status_frame.pack_propagate(False)
        self.pump_status_frame.pack(side=tk.RIGHT, fill="both", expand=True)

        # Create the status labels and dots
        self.controller_status_label = tk.CTkLabel(self.controller_status_frame, text="Controller Status:")
        self.controller_status_label.pack(anchor="center")
        self.controller_status_label.configure(font=("Helvetica", 16))

        self.status_dot_controller = tk.CTkCanvas(self.controller_status_frame, width=30, height=30, bg="#2b2b2b",  highlightthickness=0)
        self.status_dot_controller.create_oval(2, 2, 28, 28)
        self.status_dot_controller.pack(anchor="center")

        self.pump_status_label = tk.CTkLabel(self.pump_status_frame, text="Pump Status:")
        self.pump_status_label.pack(anchor="center")
        self.pump_status_label.configure(font=("Helvetica", 16))

        self.status_dot_pump = tk.CTkCanvas(self.pump_status_frame, width=30, height=30, bg="#2b2b2b", highlightthickness=0)
        self.status_dot_pump.create_oval(2, 2, 28, 28)
        self.status_dot_pump.pack(anchor="center")

        # Create pump volume label
        self.pump_volume_label = tk.CTkLabel(self.pump_status_frame, text="Pump Volume: -")
        self.pump_volume_label.pack(anchor="center")
        self.pump_volume_label.configure(font=("Helvetica", 16))

        # Start periodic check for controller and pump statuses
        self.check_controller_status()
        self.check_pump_status()
        self.update_pump_volume()

    def check_controller_status(self):
        if self.controller.is_running:
            color = 'green'
        else:
            color = 'red'
        self.status_dot_controller.create_oval(2, 2, 28, 28, fill=color)
        self.after(2000, self.check_controller_status)

    def check_pump_status(self):
        if self.pump.is_connected() and not self.pump.data_queue.empty():
            color = 'green'
        else:
            color = 'red'
        self.status_dot_pump.create_oval(2, 2, 28, 28, fill=color)
        self.after(2000, self.check_pump_status)

    def update_pump_volume(self):
        pump_volume = self.pump.get_data()
        if pump_volume is not None:
            self.pump_volume_label.configure(text=f"Pump Volume: {pump_volume}")
        else:
            if self.pump.is_connected():
                self.pump_volume_label.configure(text="Pump Volume: - (Waiting for data)")
            else:
                self.pump_volume_label.configure(text="Pump Volume: - (Serial connection closed)")
        self.after(1000, self.update_pump_volume)
