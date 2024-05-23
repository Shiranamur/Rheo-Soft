from timeline import TimelineCanvas
import customtkinter as tk

class DragManager:
    def __init__(self):
        self.current_widget = None
        self.drag_box = None

    def add_dragable(self, widget):
        widget.bind("<Enter>", self.on_hover_enter)
        widget.bind("<Leave>", self.on_hover_leave)
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)

    def on_hover_enter(self, event):
        event.widget.configure(cursor="hand1")

    def on_hover_leave(self, event):
        if not self.current_widget:
            event.widget.configure(cursor="")

    def on_start(self, event):
        self.current_widget = event.widget
        self.start_x = event.x_root
        self.start_y = event.y_root

        self.drag_box = tk.CTkLabel(self.current_widget.master, text=self.current_widget.cget("text"), fg_color="gray", text_color="white")
        self.drag_box.place(x=event.x_root, y=event.y_root, anchor="center")
        self.current_widget.configure(cursor="hand1")

    def on_drag(self, event):
        if self.drag_box is None:
            return
        new_x = event.x_root
        new_y = event.y_root
        self.drag_box.place(x=new_x, y=new_y, anchor="center")

    def on_drop(self, event):
        if self.drag_box is None:
            return
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        if target:
            current = target
            while current:
                if isinstance(current, TimelineCanvas):
                    sequence_text = self.current_widget.cget("text")
                    current.add_sequence(sequence_text)
                    break
                current = current.master
        self.drag_box.destroy()
        self.drag_box = None
        self.current_widget.configure(cursor="")
        self.current_widget = None
