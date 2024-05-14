import tkinter as tk
from jsonLoader import sequences_reader


class TimelineCanvas(tk.Canvas):
    def __init__(self, master, height):
        super().__init__(master, height=height)
        self.range = 100000
        self.zoom_level = 10
        self.visible_range = self.range * (self.zoom_level / 100)
        self.display_start = 0

        self.sequences_list = []
        self.all_sequences = None

        self.scrollbar = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=self.scroll)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.configure(xscrollcommand=self.scrollbar.set)

        self.draw_timeline()

    def scroll(self, *args):
        if len(args) == 2:
            action, value = args
            if action == "moveto":
                new_start = float(value) * (self.range - self.visible_range)
                self.display_start = max(0, min(new_start, self.range - self.visible_range))
                self.update_scroll_region()
                self.draw_timeline()

    def update_scroll_region(self):
        if self.range > 0:
            scrollbar_start = self.display_start / self.range
            scroll_end = (self.display_start + self.visible_range) / self.range
            self.scrollbar.set(scrollbar_start, min(scroll_end, 1))

    def update_range(self):
        total_duration = sum(int(seq["Duration"]) for seq in self.sequences_list)
        self.range = total_duration * 1.05

    def draw_timeline(self):
        self.delete("all")
        start = int(self.display_start)
        end = int(self.display_start + self.visible_range)
        interval = self.find_interval(self.visible_range)
        # if self.range > 0:
        #     interval = self.find_interval()
        #     for i in range(0, self.range, interval):
        #         self.create_line(i, 0, i, 15, fill="gray")
        for i in range(start, end, interval):
            x = (i - start) * (self.winfo_width() / self.visible_range)
            self.create_line(x, 0, x, 15, fill="gray")
            self.create_text(x, 20, text=str(i))

    def find_interval(self, visible_range):
        # Adjust interval based on visible range
        if visible_range > 0:
            step = int(visible_range / 10)  # Example: divide visible range into 10 parts
            return max(1, step)  # Ensure non-zero interval
        return 100  # Default interval if range is very small or zero

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
