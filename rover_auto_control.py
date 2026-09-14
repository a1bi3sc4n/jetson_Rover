import serial
import json
import time

class Rover:
    def __init__(self, port='/dev/ttyUSB0', baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.ser.reset_input_buffer()
        time.sleep(0.5)
        #Chassis config
        self.send({"T": 900, "main": 2, "module": 0})
        time.sleep(0.2)
        print("Rover connected")

    def send(self, cmd):
        self.ser.write((json.dumps(cmd) + '\n').encode())

    def drive(self, left, right):
        """left and right speed varies from -0.5 to 0.5"""
        self.send({"T": 1, "L": round(left, 3), "R": round(right, 3)})

    def stop(self):
        self.drive(0, 0)

    def close(self):
        self.stop()
        self.ser.close()                