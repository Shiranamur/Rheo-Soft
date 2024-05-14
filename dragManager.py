class DragManager():
    def __init__(self):
        self.current_widget = None

    def add_dragable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)
        widget.configure(cursor="hand1")

    def on_start(self, event):
        self.current_widget = event.widget
        self.original_x = event.x
        self.original_y = event.y

    def on_drag(self, event):
        x = self.current_widget.winfo_x() + (event.x - self.original_x)
        y = self.current_widget.winfo_y() + (event.y - self.original_y)
        self.current_widget.place(x=x, y=y)

    def on_drop(self, event):
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        if isinstance(target) and self.current_widget is not None:
            sequence_text = self.current_widget.cget("text")
            sequence_duration = self.current_widget.sequence_duration  # Ensure this attribute is set
            target.add_sequence(sequence_text, sequence_duration)
        elif isinstance(target) and self.current_widget is not None:
            target.load_sequences()  # Refresh the SequenceLib content
        self.current_widget = None
