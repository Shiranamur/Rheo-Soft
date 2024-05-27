import serial
import time

# Replace 'COM3' with the correct port for your Arduino
# For Linux or macOS, it might be something like '/dev/ttyUSB0' or '/dev/ttyACM0'
arduino_port = '/dev/ttyACM0'
baud_rate = 9600
timeout = 10  # Timeout for serial read in seconds

# Open the serial port
ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)

# Allow some time for the serial connection to establish
time.sleep(2)

print("Reading EEPROM data from Arduino...")

try:
    while True:
        if ser.in_waiting > 0:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            # Print the received line
            print(line)

except KeyboardInterrupt:
    print("Exiting program")

finally:
    ser.close()
    print("Serial port closed")
