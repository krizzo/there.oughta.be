import serial

with serial.Serial('/dev/ttyACM0', 9600, timeout=1) as ser:
    ser.write(b'\x88\x33\x0f\x00\x00\x00\x0f\x00\x00\x00')
    response = ser.read(10)
    print(" ".join(hex(c) for c in response)) 
