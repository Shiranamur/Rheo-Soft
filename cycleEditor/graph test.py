import customtkinter as tk
import math
import json
import os


class GraphFrame(tk.CTkFrame):
    def __init__(self, master, sequences_list, height, width):
        super().__init__(master, height=height, width=width)
        self.sequences_list = sequences_list

        self.resolution_label = tk.CTkLabel(self, text="Resolution (seconds):")
        self.resolution_label.pack(side=tk.BOTTOM, padx=5, pady=5)
        self.resolution_entry = tk.CTkEntry(self)
        self.resolution_entry.pack(side=tk.BOTTOM, padx=5, pady=5)

        self.update_button = tk.CTkButton(self, text="Update Graph", command=self.plot_graph)
        self.update_button.pack(side=tk.BOTTOM, padx=5, pady=5)

        self.graph_canvas = tk.CTkCanvas(self, bg="white", width=width, height=height)
        self.graph_canvas.pack(side=tk.TOP, padx=5, pady=5)

        self.plot_graph()

    def plot_graph(self):
        self.graph_canvas.delete("all")
        resolution = self.get_resolution()
        sequences = self.sequences_list

        if not sequences:
            return

        max_time = max(seq["start_time"] + int(seq["Duration"]) for seq in sequences)
        max_value = 0

        for seq in sequences:
            start_time = seq["start_time"]
            duration = int(seq["Duration"])
            end_time = start_time + duration
            function = seq.get("Function", "0")

            for t in range(start_time, end_time, resolution):
                value = self.evaluate_function(function, t, duration)
                if value > max_value:
                    max_value = value

        if max_value == 0:
            max_value = 1

        padding = 50
        canvas_width = self.graph_canvas.winfo_width()
        canvas_height = self.graph_canvas.winfo_height()
        self.graph_canvas.create_line(padding, canvas_height - padding, canvas_width - padding, canvas_height - padding,
                                      arrow=tk.LAST)  # X axis
        self.graph_canvas.create_line(padding, canvas_height - padding, padding, padding, arrow=tk.LAST)  # Y axis

        self.graph_canvas.create_text(padding / 2, padding / 2, text="Function Value", angle=90)
        self.graph_canvas.create_text(canvas_width - padding / 2, canvas_height - padding / 2, text="Time")

        for seq in sequences:
            start_time = seq["start_time"]
            duration = int(seq["Duration"])
            end_time = start_time + duration
            function = seq.get("Function", "0")

            previous_x, previous_y = None, None

            for t in range(start_time, end_time + 1, resolution):
                x = padding + (t / max_time) * (canvas_width - 2 * padding)
                value = self.evaluate_function(function, t, duration)
                y = canvas_height - padding - (value / max_value) * (canvas_height - 2 * padding)

                if previous_x is not None and previous_y is not None:
                    self.graph_canvas.create_line(previous_x, previous_y, x, y, fill="blue")

                previous_x, previous_y = x, y

    def evaluate_function(self, function, t, duration):
        try:
            value = eval(function, {"t": t, "duration": duration, "math": math})
            return value
        except:
            return 0

    def get_resolution(self):
        try:
            return int(self.resolution_entry.get())
        except ValueError:
            return 1  # Default resolution if input is invalid


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sequences_file = os.path.join(base_dir, '..', 'data', 'sequences.json')

    with open(sequences_file, "r") as f:
        sequences = json.load(f)

    for i, seq in enumerate(sequences):
        seq["start_time"] = sum(int(s["Duration"]) for s in sequences[:i])

    root = tk.CTk()
    graph_frame = GraphFrame(root, sequences, height=400, width=600)
    graph_frame.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
