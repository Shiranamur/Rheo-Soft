from timeline import TimelineCanvas


class DragManager:
    def __init__(self):
        self.current_widget = None

    def add_dragable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)
        widget.configure(cursor="hand1")
        print(f"Added dragable to {widget}")

    def on_start(self, event):
        self.current_widget = event.widget
        self.original_x = event.x
        self.original_y = event.y
        print(f"Drag started on {self.current_widget} at ({self.original_x}, {self.original_y})")

    def on_drag(self, event):
        if self.current_widget is None:
            return
        x = self.current_widget.winfo_x() + (event.x - self.original_x)
        y = self.current_widget.winfo_y() + (event.y - self.original_y)
        self.current_widget.place(x=x, y=y)
        print(f"Dragging {self.current_widget} to ({x}, {y})")

    def on_drop(self, event):
        if self.current_widget is None:
            print("No widget to drop")
            return

        x, y = event.widget.winfo_pointerxy()
        print(f"Drop coordinates: ({x}, {y})")

        target = event.widget.winfo_containing(x, y)
        if target:
            print(f"Target widget at drop: {target}")
            # Print parent hierarchy
            current = target
            while current:
                print(f"Widget: {current}, Type: {type(current)}")
                if isinstance(current, TimelineCanvas):
                    sequence_text = self.current_widget.cget("text")
                    current.add_sequence(sequence_text)
                    print(f"Dropped {sequence_text} on {current}")
                    break
                current = current.master
            else:
                print("Drop target is not a TimelineCanvas")
        else:
            print("No target widget found at drop coordinates")

        self.current_widget = None
