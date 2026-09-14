import serial
import json
import time
import threading
from pynput import keyboard



#Configuration
PORT = '/dev/ttyUSB0'
BAUD=115200
MAX_SPEED = 0.35

ser = serial.Serial(PORT, BAUD, timeout=0.1)
ser.reset_input_buffer()

CURRENT_L = 0.0
CURRENT_R = 0.0
speed = 0.25
running = True

def send_speeds(L, R):
    cmd = {"T": 1, "L": round(L, 3), "R": round(R, 3)}
    ser.write((json.dumps(cmd) + '\n').encode())

def stop():
    global CURRENT_L, CURRENT_R
    CURRENT_L = 0.0
    CURRENT_R = 0.0
    send_speeds(0, 0)

def on_press(key):
    global CURRENT_L, CURRENT_R, speed

    try:
        k = key.char.lower()
    except AttributeError:
        k = key

    if k == 'w' or k == keyboard.Key.up:
        CURRENT_L = speed
        CURRENT_R = speed
    elif k == 's' or k == keyboard.Key.down:
        CURRENT_L = -speed
        CURRENT_R = -speed
    elif k == 'a' or k == keyboard.Key.left:
        CURRENT_L = -speed * 0.8
        CURRENT_R = speed * 0.8
    elif k == 'a' or k == keyboard.Key.right:
        CURRENT_L = speed * 0.8
        CURRENT_R = -speed * 0.8
    elif k == 'q' or k == keyboard.Key.esc:
        global running
        running = False
        return False
    elif k == ' ':
        stop()
        return

    send_speeds(CURRENT_L, CURRENT_R)


def on_release(key):
    stop()


def control_loop():
    while running:
        time.sleep(0.5)


if __name__ == "__main__":
    print("Rover Keyboard Teleop")
    print("---------------------")
    print("W : forward")
    print("S: backward")


    ser.write((json.dumps({"T":900, "main":2, "module":0}) + '\n').encode())

    time.sleep(0.3)

    listrener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listrener.start()

    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        stop()
        ser.close()
        print("\n Stopped and closed serial")

