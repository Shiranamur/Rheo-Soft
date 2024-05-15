import customtkinter as tk


class TimelineCanvas(tk.CTkCanvas):
    def __init__(self, master, height, initial_scale=1, base_major=45, base_minor=7.5, base_max_range=675):
        super().__init__(master, height=height)
        self.configure(relief="flat")
        self.base_major = base_major
        self.base_minor = base_minor
        self.base_max_range = base_max_range
        self.scale = initial_scale
        self.sequences = []

        self.update_scale_properties()

        # Scrollbar setup
        self.hbar = tk.CTkScrollbar(master, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.xview)
        self.config(xscrollcommand=self.hbar.set)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Zoom buttons
        zoom_in_button = tk.CTkButton(master, text="+", command=self.zoom_in)
        zoom_in_button.pack(side=tk.RIGHT)
        zoom_out_button = tk.CTkButton(master, text="-", command=self.zoom_out)
        zoom_out_button.pack(side=tk.RIGHT)

        # Initial drawing of the timeline
        self.draw_timeline()

    def update_scale_properties(self):
        factor = 4 ** (self.scale - 1)
        self.major = self.base_major * factor
        self.minor = self.base_minor * factor
        self.max_range = self.base_max_range * factor

    def draw_timeline(self):
        self.delete("all")
        for i in range(0, int(self.max_range), int(self.minor)):
            x = i
            self.create_line(x, 0, x, 15, fill="gray")  # Minor markers
            if i % int(self.major) == 0:  # Major markers
                self.create_line(x, 10, x, 30, fill="black")
                self.create_text(x, -10, text=str(i), anchor=tk.N)
        self.config(scrollregion=self.bbox("all"))

    def zoom_in(self):
        if self.scale < 5:  # Assuming a maximum scale limit
            self.scale += 1
            self.update_scale_properties()
            self.draw_timeline()

    def zoom_out(self):
        if self.scale > 1:  # Ensuring the scale does not go below the initial scale
            self.scale -= 1
            self.update_scale_properties()
            self.draw_timeline()

    def add_sequence(self, sequence_text):
        x, y = self.winfo_pointerxy()
        x = self.canvasx(x)  # Convert screen x to canvas x
        nearest_marker = round(x / self.scale) * self.scale
        label_id = self.create_text(nearest_marker, 50, text=sequence_text, anchor=tk.NW)
        self.sequences.append({
            'id': label_id,
            'name': sequence_text,
            'start_time': nearest_marker / self.scale  # Convert pixels back to time units
        })
        # self.update_data_file()
