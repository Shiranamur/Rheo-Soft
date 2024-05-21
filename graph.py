import customtkinter as tk
import math

class GraphFrame(tk.CTkFrame):
    def __init__(self, master, sequences_list, height, width):
        super().__init__(master, height=height, width=width)
        self.sequences_list = sequences_list

        # Input box for resolution
        self.resolution_label = tk.CTkLabel(self, text="Resolution (seconds):")
        self.resolution_label.pack(side=tk.BOTTOM, padx=5, pady=5)
        self.resolution_entry = tk.CTkEntry(self)
        self.resolution_entry.pack(side=tk.BOTTOM, padx=5, pady=5)

        # Button to update the graph
        self.update_button = tk.CTkButton(self, text="Update Graph", command=self.plot_graph)
        self.update_button.pack(side=tk.BOTTOM, padx=5, pady=5)

        # Canvas to draw the graph
        self.graph_canvas = tk.CTkCanvas(self, bg="white", width=width, height=height)
        self.graph_canvas.pack(side=tk.TOP, padx=5, pady=5)

        self.plot_graph()  # Initial plot

    def plot_graph(self):
        self.graph_canvas.delete("all")
        resolution = self.get_resolution()
        sequences = self.sequences_list

        # Determine the max time and function value range
        if not sequences:
            return

        max_time = max(seq["start_time"] + int(seq["Duration"]) for seq in sequences)
        max_value = 0  # To determine the maximum value of the function

        # Evaluate all functions to find the maximum value
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
            max_value = 1  # Avoid division by zero

        # Draw axes
        padding = 50
        canvas_width = self.graph_canvas.winfo_width()
        canvas_height = self.graph_canvas.winfo_height()
        self.graph_canvas.create_line(padding, canvas_height - padding, canvas_width - padding, canvas_height - padding,
                                      arrow=tk.LAST)  # X axis
        self.graph_canvas.create_line(padding, canvas_height - padding, padding, padding, arrow=tk.LAST)  # Y axis

        # Label axes
        self.graph_canvas.create_text(padding / 2, padding / 2, text="Function Value", angle=90)
        self.graph_canvas.create_text(canvas_width - padding / 2, canvas_height - padding / 2, text="Time")

        # Plot points
        for seq in sequences:
            start_time = seq["start_time"]
            duration = int(seq["Duration"])
            end_time = start_time + duration
            function = seq.get("Function", "0")

            for t in range(start_time, end_time, resolution):
                x = padding + (t / max_time) * (canvas_width - 2 * padding)
                value = self.evaluate_function(function, t, duration)
                y = canvas_height - padding - (value / max_value) * (canvas_height - 2 * padding)
                self.graph_canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="blue")

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
