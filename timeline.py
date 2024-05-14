import tkinter as tk

class TimelineCanvas(tk.Canvas):
    def __init__(self, master, height, initial_scale=10):
        super().__init__(master, height=height)
        self.configure(relief="flat")
        self.scale = initial_scale

        # Horizontal Scrollbar
        self.hbar = tk.Scrollbar(master, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.xview)
        self.config(xscrollcommand=self.hbar.set)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Buttons for scaling
        zoom_in_button = tk.Button(master, text="+", command=self.zoom_in)
        zoom_in_button.pack(side=tk.LEFT)
        zoom_out_button = tk.Button(master, text="-", command=self.zoom_out)
        zoom_out_button.pack(side=tk.LEFT)

        # Initial drawing of the timeline
        self.draw_timeline()

    def draw_timeline(self):
        self.delete("all")
        marker_interval = self.calculate_marker_interval()
        for i in range(0, 1000, marker_interval['minor']):
            x = i * self.scale
            self.create_line(x, 0, x, 50, fill="gray")  # Minor markers
            if i % marker_interval['major'] == 0:  # Major markers
                self.create_line(x, 0, x, 100, fill="black")
                self.create_text(x, 110, text=str(i), anchor=tk.N)
        self.config(scrollregion=self.bbox("all"))

    def set_scale(self, new_scale):
        if 1 <= new_scale <= 100:  # Ensuring scale stays within a reasonable range
            self.scale = new_scale
            self.draw_timeline()

    def zoom_in(self):
        self.set_scale(self.scale * 1.5)

    def zoom_out(self):
        self.set_scale(self.scale / 1.5)

    def calculate_marker_interval(self):
        if self.scale < 5:
            return {'minor': 10, 'major': 50}
        elif self.scale < 20:
            return {'minor': 5, 'major': 25}
        else:
            return {'minor': 1, 'major': 5}
