import customtkinter as ctk
import tkinter as tk

class SeqOptMenu:
    def __init__(self, sequences_list, timeline_canvas):
        self.sequences_list = sequences_list
        self.timeline_canvas = timeline_canvas
        self.menu = tk.Menu(self.timeline_canvas, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_sequence)
        self.menu.add_command(label="Modify", command=self.modify_sequence)

    def add_menu(self, rectangle_tag):
        self.timeline_canvas.tag_bind(rectangle_tag, "<Button-3>", self.open_menu)

    def open_menu(self, event):
        self.current_rectangle = self.timeline_canvas.find_withtag(ctk.CURRENT)[0]
        self.menu.post(event.x_root, event.y_root)

    def delete_sequence(self):
        rect_index = int(self.timeline_canvas.gettags(self.current_rectangle)[0].split('_')[1])
        del self.sequences_list[rect_index]
        self.timeline_canvas.delete("all")
        self.timeline_canvas.draw_timeline()

    def modify_sequence(self):
        rect_index = int(self.timeline_canvas.gettags(self.current_rectangle)[0].split('_')[1])
        sequence = self.sequences_list[rect_index]

        modify_window = ctk.CTkToplevel(self.timeline_canvas)
        modify_window.title("Modify Sequence")

        ctk.CTkLabel(modify_window, text="Name:").grid(row=0, column=0)
        name_entry = ctk.CTkEntry(modify_window)
        name_entry.grid(row=0, column=1)
        name_entry.insert(0, sequence["Name"])

        ctk.CTkLabel(modify_window, text="Duration:").grid(row=1, column=0)
        duration_entry = ctk.CTkEntry(modify_window)
        duration_entry.grid(row=1, column=1)
        duration_entry.insert(0, sequence["Duration"])

        ctk.CTkLabel(modify_window, text="Start Time:").grid(row=2, column=0)
        start_time_entry = ctk.CTkEntry(modify_window)
        start_time_entry.grid(row=2, column=1)
        start_time_entry.insert(0, sequence["start_time"])

        def save_changes():
            sequence["Name"] = name_entry.get()
            sequence["Duration"] = int(duration_entry.get())
            sequence["start_time"] = int(start_time_entry.get())
            self.timeline_canvas.delete("all")
            self.timeline_canvas.draw_timeline()
            modify_window.destroy()

        ctk.CTkButton(modify_window, text="OK", command=save_changes).grid(row=3, columnspan=2)
