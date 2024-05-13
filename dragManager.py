class DragManager():
    def __init__(self):
        self.current_widget = None

    def add_dragable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)
        widget.configure(cursor="hand1")

    def on_start(self, event):
        # Store reference to the widget being dragged
        self.current_widget = event.widget

    def on_drag(self, event):
        # Here, you could update the position of a floating window or ghost image
        pass

    def on_drop(self, event):
        # Check if the drop target is a Timeline instance and perform the addition
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        if isinstance(target, Timeline) and self.current_widget is not None:
            sequence_attribute = self.current_widget.cget("text")
            target.add_sequence(sequence_attribute)
        self.current_widget = None  # Clear the reference after dropping
