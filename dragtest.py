import customtkinter as tk
from dragManager import DragManager
from timeline import TimelineCanvas

class TestApp(tk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Drag and Drop Test")

        self.drag_manager = DragManager()

        self.label = tk.CTkLabel(self, text="Drag me", width=100, height=30)
        self.label.place(x=50, y=50)
        self.drag_manager.add_dragable(self.label)

        self.timeline_canvas = TimelineCanvas(self, height=200)
        self.timeline_canvas.place(x=50, y=300)

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
