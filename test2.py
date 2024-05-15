import tkinter as tk


class CustomCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.range = 1000
        self.zoom_levels = [1, 2, 3]
        self.current_zoom_index = 0
        self.zoom_range = self.range / self.zoom_levels[self.current_zoom_index]
        self.x_scroll = tk.Scrollbar(parent, orient='horizontal', command=self.xview)
        self.configure(xscrollcommand=self.x_scroll.set)
        self.x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.draw_grid_lines()

    def draw_grid_lines(self):
        self.delete("grid_line")  # Clear existing grid lines
        line_spacing = self.zoom_range / 10  # Drawing lines every 1/10th of the zoom range
        for i in range(0, int(self.range / line_spacing) + 1):
            x = i * line_spacing
            self.create_line(x, 0, x, self.winfo_height(), tags="grid_line")

    def change_zoom(self, direction):
        if direction == 'in' and self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
        elif direction == 'out' and self.current_zoom_index > 0:
            self.current_zoom_index -= 1
        self.zoom_range = self.range / self.zoom_levels[self.current_zoom_index]
        self.draw_grid_lines()
        self.adjust_scroll_region()

    def adjust_scroll_region(self):
        self.configure(scrollregion=(0, 0, self.range, self.winfo_height()))
        # Adjust scrollbar to center view at middle of zoom_range
        mid_point = (self.zoom_range / 2) / self.range
        self.xview_moveto(mid_point - (self.zoom_range / 2) / self.range)


def create_test_environment():
    root = tk.Tk()
    canvas = CustomCanvas(root, width=800, height=600)

    # Buttons for zooming in and out
    btn_zoom_in = tk.Button(root, text="Zoom In", command=lambda: canvas.change_zoom('in'))
    btn_zoom_in.pack(side=tk.LEFT, padx=10)

    btn_zoom_out = tk.Button(root, text="Zoom Out", command=lambda: canvas.change_zoom('out'))
    btn_zoom_out.pack(side=tk.LEFT, padx=10)

    root.mainloop()

# Uncomment the line below to run the test environment when you're ready.
create_test_environment()