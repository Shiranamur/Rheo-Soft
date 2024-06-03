import serial
import time
import threading

sequences = [[5, 5], [5, 50]]
increment_var = 0
command = None
end_of_sequences = False
lock = threading.Lock()

# Configure the serial port
serial_port = '/dev/ttyUSB0'  # Replace with your serial port identifier
baud_rate = 115200
timeout = 2  # Timeout for reading from the serial port

# Initialize the serial connection with hardware flow control
ser = serial.Serial(
    port=serial_port,
    baudrate=baud_rate,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=timeout,
)

read_r68 = "$REG 68\r\n"
read_r65 = "$REG 65\r\n"
special_command = "$REG 2=0\r\n"  # Replace with your special command


def read_cycle():
    global increment_var, command, end_of_sequences
    while True:
        for seq in sequences:
            sleep_time = seq[0]
            setpoint = seq[1]
            time.sleep(sleep_time)
            with lock:
                increment_var = 1
                command = f"$REG 4={setpoint}\r\n"
            print(f"New setpoint temp : {command}")
        with lock:
            end_of_sequences = True
            break


def read_response():
    response = b""
    while True:
        chunk = ser.read_until(b'\r\n')
        response += chunk
        if b'\r\n' in chunk:
            break
    return response.decode('ascii').strip()


def send_command():
    global increment_var, command, end_of_sequences
    while True:
        t_start = time.time()

        ser.write(read_r68.encode())
        print(f"Read r68 command: {read_r68.strip()}")
        response = read_response()
        print(f"Received response: {response}")

        ser.write(read_r65.encode())
        print(f"Read r65 command: {read_r65.strip()}")
        response = read_response()
        print(f"Received response: {response}")

        with lock:
            if increment_var == 1:
                # print("Switching to increment_var = 1")
                ser.write(command.encode())
                print(f"Sent command3: {command.strip()}")
                response = read_response()
                print(f"Received response: {response}")
                increment_var = 0
                if end_of_sequences:
                    ser.write(special_command.encode())
                    print(f"Sent setpoint temp {special_command.strip()}")
                    response = read_response()
                    print(f"Received response: {response}")
                    end_of_sequences = False

        t_end = time.time()
        elapsed_time = t_end - t_start
        # print(f"While loop executed in : {elapsed_time}")
        s_time = max(0, 0.5 - elapsed_time)
        time.sleep(s_time)


# Start the test function as a separate thread
threading.Thread(target=read_cycle, daemon=True).start()

# Run the send_command function in the main thread
send_command()
