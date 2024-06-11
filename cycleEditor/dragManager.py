import customtkinter as ctk
from cycleEditor.timeline import TimelineCanvas

class DragManager:
    def __init__(self):
        self.current_widget = None
        self.drag_box = None
        self.clone = None

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

        try:
            sequence_name = self.current_widget.sequence_name
        except AttributeError:
            sequence_name = ""

        self.drag_box = ctk.CTkFrame(self.current_widget.master, fg_color="gray")
        self.drag_box.place(x=event.x_root, y=event.y_root, anchor="center")
        self.current_widget.configure(cursor="hand1")

        # Create a clone of the current widget
        self.clone = ctk.CTkFrame(self.current_widget.master)
        label = ctk.CTkLabel(self.clone, text=self.current_widget.cget("text"))
        label.pack()
        self.clone.place(x=event.x_root, y=event.y_root, anchor="center")

    def on_drag(self, event):
        if self.clone is None:
            return
        new_x = event.x_root
        new_y = event.y_root
        self.clone.place(x=new_x, y=new_y, anchor="center")

    def on_drop(self, event):
        if self.clone is None:
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
        self.clone.destroy()
        self.clone = None
        self.drag_box.destroy()
        self.drag_box = None
        self.current_widget.configure(cursor="")
        self.current_widget = None
