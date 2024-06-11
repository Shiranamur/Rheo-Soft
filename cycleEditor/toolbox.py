import customtkinter as ctk
from utils import jsonLoader as js
import cycleEditor.dragManager as dm
import tkinter as tk
from tkinter import ttk


class ToolboxFrame(ctk.CTkFrame):
    def __init__(self, master, width):
        super().__init__(master, width=width)
        self.tb_label = ctk.CTkLabel(self, text="TOOLBOX", justify="center", font=("Helvetica", 20), width=width,
                                     pady=5,
                                     anchor="s")
        self.tb_label.pack(side="top", fill="x")

        self.sequence_creator = SequenceCreator(self)
        self.sequence_creator.pack(side="top", fill="both", expand=False)

        self.sequence_lib_frame = ctk.CTkFrame(self)
        self.sequence_lib_frame.pack(side="bottom", fill="both", expand=True)

        self.lib_label = ctk.CTkLabel(self.sequence_lib_frame, text="Librairie de séquence", justify="center",
                                      font=("Helvetica", 15))
        self.lib_label.pack(side="top", fill="x", pady=5)

        self.sequence_lib = ScrollableSequenceLib(self.sequence_lib_frame)
        self.sequence_lib.pack(side="top", fill="both", expand=True)

        self.sequence_creator.set_sequence_lib(self.sequence_lib)


class SequenceCreator(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.sequence_lib = None  # Initialize as None
        self.label = ctk.CTkLabel(self, text="Sequence Creator", justify="center")
        self.label.pack(side="top", pady=5)

        self.name_label = ctk.CTkLabel(self, text="Nom de la séquence :", justify="left")
        self.name_label.pack(side="top", pady=5)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(side="top", pady=5)

        self.duration_label = ctk.CTkLabel(self, text="Durée de la séquence (en secondes):")
        self.duration_label.pack(side="top", pady=5)
        self.duration_entry = ctk.CTkEntry(self)
        self.duration_entry.pack(side="top", pady=5)

        self.function_label = ctk.CTkLabel(self, text="Fonction:")
        self.function_label.pack(side="top", pady=5)
        self.function_entry = ctk.CTkEntry(self)
        self.function_entry.pack(side="top", pady=5)

        self.create_button = ctk.CTkButton(self, text="Create Sequence", command=self.verify_sequence)
        self.create_button.pack(side="top", pady=10)

        self.status_label = ctk.CTkLabel(self, text="")
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


class ScrollableSequenceLib(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # Store a reference to the master window
        self.frames = {}
        self.load_sequences()
        self.create_context_menu()

    def load_sequences(self):
        self.clear_frames()
        sequences = js.sequences_reader()
        for sequence in sequences:
            sequence_name = sequence["Name"]
            frame = ttk.LabelFrame(self, text=sequence_name, height=25, labelanchor='n')
            frame.pack(side="top", pady=7, fill="x", padx=5)
            frame.config(relief="flat", borderwidth=0)  # Remove border and relief

            # Center the label text
            style = ttk.Style()
            style.configure("TLabelframe.Label", anchor="center")

            frame.sequence_name = sequence_name  # Store sequence name as an attribute of the frame

            self.frames[sequence_name] = frame
            dm.DragManager().add_dragable(frame)
            frame.bind("<Button-3>", self.show_context_menu)  # Right-click event

    def clear_frames(self):
        for frame in self.frames.values():
            frame.destroy()
        self.frames.clear()

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.show_delete_confirmation)
        self.context_menu.add_command(label="Cancel", command=self.cancel_context_menu)

    def show_context_menu(self, event):
        self.current_frame = event.widget
        self.context_menu.post(event.x_root, event.y_root)

    def cancel_context_menu(self):
        self.context_menu.unpost()

    def show_delete_confirmation(self):
        self.context_menu.unpost()  # Hide the context menu

        # Create a confirmation dialog
        self.confirmation_dialog = ctk.CTkToplevel(self.master)
        self.confirmation_dialog.title("Confirmer la suppression")

        # Set the size of the confirmation dialog
        dialog_width = 320
        dialog_height = 120
        self.confirmation_dialog.geometry(f"{dialog_width}x{dialog_height}")

        # Center the confirmation dialog on the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        self.confirmation_dialog.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(self.confirmation_dialog, text="Êtes-vous sur de vouloir supprimer cette séquence ?")
        label.pack(pady=20)

        button_frame = ctk.CTkFrame(self.confirmation_dialog)
        button_frame.pack(pady=10)

        yes_button = ctk.CTkButton(button_frame, text="Yes", command=self.delete_sequence)
        yes_button.pack(side="left", padx=10)

        no_button = ctk.CTkButton(button_frame, text="No", command=self.cancel_delete)
        no_button.pack(side="right", padx=10)

    def cancel_delete(self):
        self.confirmation_dialog.destroy()  # Close the confirmation dialog

    def delete_sequence(self):
        sequence_name = self.current_frame.sequence_name

        sequences = js.sequences_reader()
        sequences = [seq for seq in sequences if seq["Name"] != sequence_name]
        js.sequences_writer(sequences)

        self.load_sequences()

        self.confirmation_dialog.destroy()
