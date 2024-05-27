import customtkinter as tk
from utils import jsonLoader as js
import cycleEditor.dragManager as dm


class ToolboxFrame(tk.CTkFrame):
    def __init__(self, master, width):
        super().__init__(master, width=width)
        self.tb_label = tk.CTkLabel(self, text="TOOLBOX", justify="center", font=("Helvetica", 20), width=width, pady=5,
                                    anchor="s")
        self.tb_label.pack(side="top", fill="x")

        self.sequence_creator = SequenceCreator(self)
        self.sequence_creator.pack(side="top", fill="both", expand=False)

        self.sequence_lib_frame = tk.CTkFrame(self)
        self.sequence_lib_frame.pack(side="bottom", fill="both", expand=True)

        self.lib_label = tk.CTkLabel(self.sequence_lib_frame, text="Librairie de séquence", justify="center",
                                     font=("Helvetica", 15))
        self.lib_label.pack(side="top", fill="x", pady=5)

        self.sequence_lib = ScrollableSequenceLib(self.sequence_lib_frame)
        self.sequence_lib.pack(side="top", fill="both", expand=True)

        self.sequence_creator.set_sequence_lib(self.sequence_lib)


class SequenceCreator(tk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.sequence_lib = None  # Initialize as None
        self.label = tk.CTkLabel(self, text="Sequence Creator", justify="center")
        self.label.pack(side="top", pady=5)

        self.name_label = tk.CTkLabel(self, text="Nom de la séquence :", justify="left")
        self.name_label.pack(side="top", pady=5)
        self.name_entry = tk.CTkEntry(self)
        self.name_entry.pack(side="top", pady=5)

        self.duration_label = tk.CTkLabel(self, text="Durée de la séquence (en secondes):")
        self.duration_label.pack(side="top", pady=5)
        self.duration_entry = tk.CTkEntry(self)
        self.duration_entry.pack(side="top", pady=5)

        self.function_label = tk.CTkLabel(self, text="Fonction:")
        self.function_label.pack(side="top", pady=5)
        self.function_entry = tk.CTkEntry(self)
        self.function_entry.pack(side="top", pady=5)

        self.create_button = tk.CTkButton(self, text="Create Sequence", command=self.verify_sequence)
        self.create_button.pack(side="top", pady=10)

        self.status_label = tk.CTkLabel(self, text="")
        self.status_label.pack(side="top", pady=5)

    def set_sequence_lib(self, sequence_lib):
        self.sequence_lib = sequence_lib

    def verify_sequence(self):
        if not self.duration_entry.get().isdigit():
            self.status_label["text"] = "La durée saisie est invalide"
        elif not self.name_entry.get():
            self.status_label["text"] = "Le nom de la sequence est invalide"
        else:
            self.create_sequence()

    def create_sequence(self):
        name = self.name_entry.get()
        duration = self.duration_entry.get()
        function = self.function_entry.get()
        sequence_data = {
            "Name": name,
            "Duration": duration,
            "Function": function
        }

        sequence_list = js.sequences_reader()
        sequence_list.append(sequence_data)
        self.status_label["text"] = js.sequences_writer(sequence_list)
        if self.sequence_lib:
            self.sequence_lib.load_sequences()


class ScrollableSequenceLib(tk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.labels = {}
        self.load_sequences()

    def load_sequences(self):
        self.clear_labels()
        for sequence in js.sequences_reader():
            sequence_name = sequence["Name"]
            label = tk.CTkLabel(self, text=sequence_name)
            label.pack(side="top", pady=10, fill="x", padx=5)
            self.labels[sequence_name] = label
            dm.DragManager().add_dragable(label)

    def clear_labels(self):
        for label in self.labels.values():
            label.destroy()
        self.labels.clear()
