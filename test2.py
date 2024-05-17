import customtkinter as tk


class TimelineCanvas(tk.CTkCanvas):
    def __init__(self, master, height):
        super().__init__(master, height=height)
        self.range = 10000
        self.var_zoom = tk.IntVar(value=1)
        self.visible_range = self.range / self.var_zoom.get()
        self.height = height

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
        step = 1000
        padding = 25
        num_steps = (self.range // step) + 1
        for i in range(num_steps):
            x = padding + i * ((self.visible_range - 2 * padding) / (num_steps - 1))
            self.create_line(x, 0, x, self.height - 30, tags="line")
            self.create_text(x, self.height - 20, text=str(i * step), anchor=tk.N, tags="text")

    def update_zoom(self):
        oldpos = self.xview()
        focus_point = (oldpos[1] - oldpos[0]) / 2
        print(f"oldpos: {oldpos}, focus_point: {focus_point}")

        self.visible_range = self.range / self.var_zoom.get()

        self.configure(scrollregion=(0, 0, self.visible_range, self.height))
        self.draw_timeline()

        newpos = self.xview()
        newpos_halved = (newpos[1] - newpos[0])/2
        print(f"newpos: {newpos}, newpos_halved: {newpos_halved}\n moveto: {focus_point-newpos_halved}")

        self.scrollbar.configure(command=self.xview)
        self.xview_moveto(max(0, min(focus_point-newpos_halved, 1)))

    def zoom_in(self):
        if self.var_zoom.get() < 5:
            self.var_zoom.set(self.var_zoom.get() + 1)
            self.update_zoom()

    def zoom_out(self):
        if self.var_zoom.get() > 1:
            self.var_zoom.set(self.var_zoom.get() - 1)
            self.update_zoom()
