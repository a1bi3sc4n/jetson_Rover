import serial
import json
import time

PORT = '/dev/ttyUSB0'   # ← change this to whatever appeared

ser = serial.Serial(PORT, 115200, timeout=1)
ser.reset_input_buffer()

print(f"Connected to {PORT}")

# Configure + move
ser.write((json.dumps({"T":900, "main":2, "module":0}) + '\n').encode())
time.sleep(0.4)

print("Sending move command...")
ser.write((json.dumps({"T":1, "L":0.3, "R":0.3}) + '\n').encode())
time.sleep(5)

ser.write((json.dumps({"T":1, "L":0, "R":0}) + '\n').encode())

print("Listening for reply...")
time.sleep(1)
data = ser.read(300)
print("Raw reply:", data)
print("Text:", data.decode(errors='replace') if data else "No reply")

ser.close()