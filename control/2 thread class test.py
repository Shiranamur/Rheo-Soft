import customtkinter as tk
import time
import threading

class Test():
    def __init__(self):
        self.read_r68 = "$REG 68 = \r\n"
        self.read_r65 = "$REG 65 = \r\n"
        self.set_temp = ''
        self.end_command = "$REG 2=0\r\n"
        self.start_command = "$REG 2=1\r\n"

        self.r68_reply = "r68 reply"
        self.r65_reply = "r65 reply"
        self.end_reply = "$REG 2 now at 0\r\n"
        self.start_reply = "$REG 2 now at 1\r\n"

        self.sequences = [[5, 5], [5, 50],[5, 5], [5, 50],[5, 5], [5, 50],[5, 5], [5, 50]]

        self.setpoint_boolean = 0
        self.end_of_seq_boolean = 0
        self.lock = threading.Lock()

    def read_cycle(self):
        while True:
            for seq in self.sequences:
                tts = seq[0]  # time to sleep
                temp = seq[1]
                time.sleep(tts)
                with self.lock:
                    self.setpoint_boolean += 1
                    self.set_temp = f"$REG 4 = {temp}\r\n"
                    print(f"temp set to : {temp} with command : {self.set_temp}")

            with self.lock:
                self.end_of_seq_boolean += 1
                print("End of sequence list")
                break

    def temp_read(self):
        while True:
            with self.lock:
                if self.setpoint_boolean > 0:
                    print("Setpoint boolean > 0")
                    print(f"Received command: {self.set_temp}")
                    self.setpoint_boolean -= 1
                elif self.end_of_seq_boolean > 0:
                    print(f"Received command: {self.end_command}")
                    self.end_of_seq_boolean -= 1
                    break
                else:
                    print(f"Received command: {self.read_r68}")
                    print(f"Replying with: {self.r68_reply}")
                    print(f"Received command: {self.read_r65}")
                    print(f"Replying with: {self.r65_reply}")
            time.sleep(1)  # simulate delay



    def start_read_cycle(test_instance):
        threading.Thread(target=test_instance.read_cycle, daemon=True).start()

    def start_temp_read(test_instance):
        threading.Thread(target=test_instance.temp_read, daemon=True).start()


def main():
    test = Test()

    root = tk.CTk()
    button = tk.CTkButton(root, text="Start read_cycle", command=test.start_read_cycle)
    button.pack()

    test.start_temp_read()

    root.mainloop()


if __name__ == "__main__":
    main()


