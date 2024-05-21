import customtkinter as tk
from jsonLoader import sequences_reader


class TimelineCanvas(tk.CTkCanvas):
    def __init__(self, master, height):
        super().__init__(master, height=height)
        self.range = 1000
        self.var_zoom = tk.IntVar(value=1)
        self.visible_range = self.range / self.var_zoom.get()
        self.height = height
        #self.zoom_dic = {1: 100, 2: 50, 3: 33, 4: 25, 5: 20}
        self.sequences_list = []

        self.scrollbar = tk.CTkScrollbar(master, orientation=tk.HORIZONTAL, command=self.xview)
        self.scrollbar.pack(side=tk.BOTTOM, fill="x")
        self.configure(xscrollcommand=self.scrollbar.set)

        self.button_frame = tk.CTkFrame(master, height=height)
        self.button_frame.pack(side=tk.RIGHT, fill="y")

        # Buttons for zooming
        self.zoom_in_button = tk.CTkButton(self.button_frame, text="Zoom In", command=self.zoom_out)
        self.zoom_in_button.pack(pady=5)
        self.zoom_out_button = tk.CTkButton(self.button_frame, text="Zoom Out", command=self.zoom_in)
        self.zoom_out_button.pack(pady=5)
        self.update_zoom()
        self.draw_timeline()

    def draw_timeline(self):
        self.delete("all")
        start = 0  # Assuming timeline starts at 0
        end = int(self.range)
        interval = self.find_interval(self.visible_range)

        padding = 25
        for i in range(start, end, interval):
            x = padding + (i - start) * ((self.visible_range - 2 * padding) / (end - start))
            self.create_line(x, 0, x, self.height - 30, tags="line")
            self.create_text(x, self.height - 20, text=str(i), anchor=tk.N, tags="text")
        self.draw_sequences()

    def find_interval(self, visible_range):
        # Adjust interval based on visible range
        if visible_range > 0:
            step = int(visible_range / 20)  # Example: divide visible range into 20 parts
            magnitude = 10 ** (len(str(step)) - 1)
            interval = max(1, (step // magnitude) * magnitude)
            return interval
        return 100  # Default interval if range is very small or zero

    def update_zoom(self):
        #oldpos = self.xview()
        #focus_point = (oldpos[1] - oldpos[0]) / 2
        #test = focus_point * (self.var_zoom.get() / 100)
        self.visible_range = self.range / self.var_zoom.get()
        self.configure(scrollregion=(0, 0, self.visible_range, self.height))
        self.draw_timeline()
        self.scrollbar.configure(command=self.xview)
        #self.xview_moveto(max(0, min(test, 1)))
        self.xview_moveto(0)

    def zoom_in(self):
        if self.var_zoom.get() < 5:
            self.var_zoom.set(self.var_zoom.get() + 1)
            self.update_zoom()

    def zoom_out(self):
        if self.var_zoom.get() > 1:
            self.var_zoom.set(self.var_zoom.get() - 1)
            self.update_zoom()

    def update_range(self):
        total_duration = sum(int(seq["Duration"]) for seq in self.sequences_list)
        self.range = total_duration * 1.05

    def add_sequence(self, sequence_name):
        self.all_sequences = sequences_reader()
        for sequence in self.all_sequences:
            if sequence.get("Name") == sequence_name:
                if not self.sequences_list:
                    start_time = 0
                else:
                    last_sequence = self.sequences_list[-1]
                    start_time = last_sequence["start_time"] + int(last_sequence["Duration"])
                sequence["start_time"] = start_time
                self.sequences_list.append(sequence)
                self.update_range()
                self.draw_timeline()
                self.all_sequences.remove(sequence)

    def draw_sequences(self):
        padding = 25
        for sequence in self.sequences_list:
            start_time = sequence["start_time"]
            duration = int(sequence["Duration"])
            end_time = start_time + duration
            x1 = padding + (start_time * (self.visible_range - 2 * padding) / self.range)
            x2 = padding + (end_time * (self.visible_range - 2 * padding) / self.range)
            self.create_rectangle(x1, 30, x2, self.height - 50, fill="gray", tags="sequence")
            self.create_text((x1 + x2) / 2, 35, text=sequence["Name"], anchor=tk.N, tags="sequence")
