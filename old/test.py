import serial
import time
# ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)


command = "R41=23.5"
ans = ",k"

def ascii2hex(var):
    hexValues = [hex(ord(c))[2:] for c in var]
    return "".join(hexValues)


def addSSbits(var):
    startChar = "24"  # $ sign in ascii, start char
    stopChar = "0D"  # line return in ascii, stop char
    hexString = ascii2hex(var)
    return startChar+hexString+stopChar

def hex2ascii():
    pass

print(addSSbits(command))

start = time.time()
time.sleep(30)
end = time.time()
print(end - start)
