import os

class AppSettings:
    title = "RheoSoft"
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, 'data')

    @staticmethod
    def default_geometry(root):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        return f'{screen_width}x{screen_height}'
