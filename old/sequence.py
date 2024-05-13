import json
import tkinter as tk


class Sequence():
    sequence_count = 0

    def __init__(self, function, name=None, duration=60):
        if name is None:
            Sequence.sequence_count += 1
            name = f"Sequence{Sequence.sequence_count}"
        self.name = name
        self.duration = duration
        self.start_time = None
        self.end_time = None
        self.function = function


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editeur de Cycle")
        self.sequences = []
        self.create_widgets()

    def create_widgets(self):
        self.topmenu = Topmenu(self)
        self.topmenu.pack(side="top", fill="x")

        self.toolbox = Toolbox(self)
        self.toolbox.pack(side="left", fill="y")



class Topmenu(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.setup_menubuttons()

    def setup_menubuttons(self):
        self.label = tk.Label(self, text="Button Panel")
        self.label.pack(side='left')

        self.button1 = tk.Button(self, text="Button 1")
        self.button1.pack(side='left', padx=5)
        self.button2 = tk.Button(self, text="Button 2")
        self.button2.pack(side='left', padx=5)


class Toolbox(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.set_label()
        self.sequence_lib = Sequencelib(self)
        self.sequence_lib.pack(side="bottom")
        self.sequence_creator = Sequencecreator(self, self.sequence_lib)
        self.sequence_creator.pack(side="top")
        self.sequence_timeline = Timeline(self)

    def set_label(self):
        self.label = tk.Label(self, text="Tool Box", justify='center')
        self.label.pack(side="top")

class Timeline(tk.Canvas):
    def __init__(self,master):
        super().__init__(master)
        self.sequence_list = []


class Sequencecreator(tk.Frame):
    def __init__(self, master, sequence_lib):
        super().__init__(master)
        self.sequence_lib = sequence_lib
        self.setup_widgets()

    def setup_widgets(self):
        self.label = tk.Label(self, text="Sequence Creator", justify='center')
        self.label.pack(side="top")

        self.name_label = tk.Label(self, text="Name:")
        self.name_label.pack(side="top")
        self.name_entry = tk.Entry(self)
        self.name_entry.pack(side="top")

        self.duration_label = tk.Label(self, text="Duration:")
        self.duration_label.pack(side="top")
        self.duration_entry = tk.Entry(self)
        self.duration_entry.pack(side="top")

        self.function_label = tk.Label(self, text="Fonction:")
        self.function_label.pack(side="top")
        self.function_entry = tk.Entry(self)
        self.function_entry.pack(side="top")

        self.create_button = tk.Button(self, text="Create Sequence", command=self.create_sequence)
        self.create_button.pack(side="top")

        self.status_label = tk.Label(self, text="")
        self.status_label.pack(side="top")

    def create_sequence(self):
        name = self.name_entry.get() if self.name_entry.get() else None
        duration = int(self.duration_entry.get()) if self.duration_entry.get().isdigit() else 60
        function = self.function_entry.get()
        sequence = Sequence(function, name, duration)
        self.save_sequence(sequence)
        self.status_label.config(text="Séquence sauvegardée")
        self.sequence_lib.refresh()  # Use the directly passed reference

    def save_sequence(self, sequence):
        sequence_data = {
            "name": sequence.name,
            "duration": sequence.duration,
            "function": sequence.function
        }

        try:
            with open('../sequences.json', 'r') as file:
                try:
                    sequences = json.load(file)
                except json.JSONDecodeError:
                    sequences = []
        except FileNotFoundError:
            sequences = []

        sequences.append(sequence_data)

        with open('../sequences.json', 'w') as file:
            json.dump(sequences, file, indent=4)


class Sequencelib(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.labels = {}
        self.load_sequences()

    def load_sequences(self):
        self.clear_labels()
        try:
            with open('../sequences.json', 'r') as file:
                sequences = json.load(file)
                for sequence in sequences:
                    label_name = sequence['name']
                    label = tk.Label(self, text=label_name)
                    label.pack(side="top")
                    self.labels[label_name] = label
        except (FileNotFoundError, json.JSONDecodeError):
            print("load failed")

    def clear_labels(self):
        for label in self.labels.values():
            label.destroy()
        self.labels.clear()

    def refresh(self):
        self.load_sequences()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
