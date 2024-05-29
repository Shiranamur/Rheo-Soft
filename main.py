# main.py
import customtkinter as tk
from settings import AppSettings
from tabview import Tabview


class Application(tk.CTk):
    def __init__(self):
        super().__init__()
        self.title(AppSettings.title)
        self.geometry(AppSettings.default_geometry(self))
        self.tabview = Tabview(master=self)
        self.tabview.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
