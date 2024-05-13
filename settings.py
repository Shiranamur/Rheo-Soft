class AppSettings:
    title = "Editeur de Cycle"

    @staticmethod
    def default_geometry(root):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        return f'{screen_width}x{screen_height}'