import customtkinter as ctk
import tkinter as tk

class SeqOptMenu:
    def __init__(self, sequences_list, timeline_canvas):
        self.sequences_list = sequences_list
        self.timeline_canvas = timeline_canvas
        self.menu = tk.Menu(self.timeline_canvas, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_sequence)
        self.menu.add_command(label="Modify", command=self.modify_sequence)
        self.modify_window = None

    def add_menu(self, rectangle_tag):
        self.timeline_canvas.tag_bind(rectangle_tag, "<Button-3>", self.open_menu)

    def open_menu(self, event):
        self.current_rectangle = self.timeline_canvas.find_withtag(ctk.CURRENT)[0]
        self.menu.post(event.x_root, event.y_root)
        self.mouse_x = event.x_root
        self.mouse_y = event.y_root

    def delete_sequence(self):
        rect_index = int(self.timeline_canvas.gettags(self.current_rectangle)[0].split('_')[1])
        del self.sequences_list[rect_index]
        self.timeline_canvas.update_range()
        self.timeline_canvas.draw_timeline()

    def modify_sequence(self):
        rect_index = int(self.timeline_canvas.gettags(self.current_rectangle)[0].split('_')[1])
        sequence = self.sequences_list[rect_index]

        self.modify_window = ctk.CTkToplevel(self.timeline_canvas)
        self.modify_window.title("Modify Sequence")
        self.modify_window.geometry(f"+{self.mouse_x}+{self.mouse_y}")  # Position the window at the mouse cursor

        ctk.CTkLabel(self.modify_window, text="Name:").grid(row=0, column=0)
        name_entry = ctk.CTkEntry(self.modify_window)
        name_entry.grid(row=0, column=1)
        name_entry.insert(0, sequence["Name"])

        ctk.CTkLabel(self.modify_window, text="Duration:").grid(row=1, column=0)
        duration_entry = ctk.CTkEntry(self.modify_window)
        duration_entry.grid(row=1, column=1)
        duration_entry.insert(0, sequence["Duration"])

        ctk.CTkLabel(self.modify_window, text="Start Time:").grid(row=2, column=0)
        start_time_entry = ctk.CTkEntry(self.modify_window)
        start_time_entry.grid(row=2, column=1)
        start_time_entry.insert(0, sequence["start_time"])

        ctk.CTkLabel(self.modify_window, text="Function:").grid(row=3, column=0)
        function_entry = ctk.CTkEntry(self.modify_window)
        function_entry.grid(row=3, column=1)
        function_entry.insert(0, sequence["Function"])

        def save_changes():
            sequence["Name"] = name_entry.get()
            sequence["Duration"] = int(duration_entry.get())
            sequence["start_time"] = int(start_time_entry.get())
            sequence["Function"] = function_entry.get()

            # Recalculate start times for all sequences
            self.recalculate_start_times()

            self.timeline_canvas.update_range()
            self.timeline_canvas.draw_timeline()
            self.modify_window.destroy()

        ctk.CTkButton(self.modify_window, text="OK", command=save_changes).grid(row=4, columnspan=2)

    def recalculate_start_times(self):
        for i in range(1, len(self.sequences_list)):
            self.sequences_list[i]["start_time"] = self.sequences_list[i-1]["start_time"] + self.sequences_list[i-1]["Duration"]
