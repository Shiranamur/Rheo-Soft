import serial
import time

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


def read_response():
    response = b""
    while True:
        chunk = ser.read_until(b'\r\n')
        response += chunk
        if b'\r\n' in chunk:
            break
    return response.decode('ascii').strip()


command = "$REG 68\r\n"
command2 = "$REG 65\r\n"

# Flush the input buffer
ser.reset_input_buffer()

# Send the first command
ser.write(command.encode())
print(f"Sent command: {command.strip()}")

# Read the response for the first command
response = read_response()
print(f"Received response: {response}")

# Send the second command if the first response was received
if response:
    ser.write(command2.encode())
    print(f"Sent command2: {command2.strip()}")

    # Read the response for the second command
    response2 = read_response()
    print(f"Received response2: {response2}")

# Close the serial connection
ser.close()
