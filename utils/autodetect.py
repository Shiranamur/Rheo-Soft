import sys
import glob
import serial
import time


def list_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        port_list = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        port_list = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        port_list = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in port_list:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def read_and_identify(port):
    """Reads data from the given port and identifies the device type."""
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=20)  # set timeout length
        data = ser.readline().decode('ascii').strip()
        ser.close()
        print(f"terminated connection to {port}")

        if data == '':
            ser = serial.Serial(port, baudrate=115200, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, timeout=30)
            command = '$ID\r\n'
            ser.write(command.encode())
            data = ser.read_until(b'\r\n').decode().strip()
            ser.close()
            print(f"terminated connection to {port}")

            if data == '':
                return 'error', port

        if 'L/min' in data:
            return 'pump', port
        elif 'ID=Junior' in data:
            return 'controller', port
        else:
            return 'unknown', port
    except (OSError, serial.SerialException) as e:
        print(f"Error with port {port}: {e}")
        return 'error', port


def identify_devices():
    """Identifies which ports are connected to the pump and the controller."""
    ports = list_serial_ports()
    print("Available ports:", ports)

    pump_port = None
    controller_port = None

    for port in ports:
        print(f"Testing port: {port}")
        device_type, port_name = read_and_identify(port)

        if device_type == 'pump':
            pump_port = port_name
            print(f"Pump found on port: {pump_port}")
        elif device_type == 'controller':
            """To be replaced with actual controller logic"""
            controller_port = port_name
            print(f"Controller found on port: {controller_port}")
    return pump_port, controller_port