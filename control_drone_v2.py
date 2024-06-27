import socket
import time
import threading
import cv2
import numpy as np
from enum import Enum
import keyboard
import pickle
from filelock import FileLock

# Define drone states


class tello_state(Enum):
    Landed = 0,
    Moving = 1,
    Hovering = 2,
    Blocked = 3,
    PersonFound = 4


# Initial state
current_state = tello_state.Landed

# Tello connection details
tello_IP = '192.168.10.1'
tello_port_cmd = 8889

host = '192.168.10.2'
host_port_cmd = 8891
host_port_state = 8890

# Connecting local host to Tello with socket
locaddr_cmd = (host, host_port_cmd)
sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address_cmd = (tello_IP, tello_port_cmd)
sock_cmd.bind(locaddr_cmd)

locaddr_state = (host, host_port_state)
sock_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_state.bind(locaddr_state)

# Load shared dictionary


def load_dict():
    try:
        with FileLock('variable_dict.pkl.lock'):
            with open('variable_dict.pkl', 'rb') as f:
                return pickle.load(f)
    except FileNotFoundError:
        return {}

# Send command to Tello drone


def do_command(cmd):
    sock_cmd.sendto(cmd.encode(encoding="utf-8"),
                    tello_address_cmd)  # Send Tello
    data, server = sock_cmd.recvfrom(1518)  # Wait response
    resp = data.decode(encoding="latin-1")
    return resp.replace("\r\n", "")

# Switch drone state


def switch_state(new_state: tello_state):
    global current_state
    print("Switching from", current_state, "to", new_state)
    current_state = new_state

# Parse state data


def parse_state_data(data):
    state_dict = {}
    for item in data.split(';'):
        if ':' in item:
            key, value = item.split(':')
            state_dict[key] = value
    return state_dict


# Receive state data
current_xspeed = 0
speeds = [0, 0, 0]


def receive_state(stop_event):
    global speeds
    last_read_time = time.time()
    while not stop_event.is_set():
        try:
            data, server = sock_state.recvfrom(1518)
            state_info = data.decode(encoding="utf-8")
            state_dict = parse_state_data(state_info)
            current_time = time.time()
            if current_time - last_read_time >= 1:  # Update speed every second
                speeds[0] = float(state_dict['vgx'])
                speeds[1] = float(state_dict['vgy'])
                speeds[2] = float(state_dict['vgz'])
                last_read_time = current_time
        except UnicodeDecodeError:
            print(f"Unicode decode error: {data}")
        except Exception as e:
            print(f"Error receiving state: {str(e)}")


retour = do_command("command")
print(f"Retour de 'command': {retour}")
etat_batterie = do_command("battery?")
print(f"Retour de 'battery?': {etat_batterie}")

# Initialize move count
movecount = 0

# Start the state thread
stop_event = threading.Event()
state_thread = threading.Thread(target=receive_state, args=(stop_event,))
state_thread.start()
print(f"Sending 'streamon': {do_command('streamon')}")

person_found_last_print_time = time.time()

while True:
    # Perform actions based on the current state
    if current_state == tello_state.Hovering:
        print(f"Sending 'forward': {do_command('forward 30')}")
        switch_state(tello_state.Moving)
        time.sleep(1)
        movecount += 1

    elif current_state == tello_state.Blocked:
        print(f"Sending 'cw': {do_command('cw 45')}")
        time.sleep(2)

    elif current_state == tello_state.Moving and speeds == [0, 0, 0]:
        switch_state(tello_state.Hovering)

    if keyboard.is_pressed('e'):
        if current_state == tello_state.Landed:
            print(f"Sending 'takeoff': {do_command('takeoff')}")
            switch_state(tello_state.Moving)

    if keyboard.is_pressed('y'):
        print(f"Sending 'land': {do_command('land')}")
        break

    # Check if too close to the wall
    dict = load_dict()
    if dict['variable'] == 1 and current_state not in [tello_state.Landed, tello_state.Blocked, tello_state.PersonFound]:
        switch_state(tello_state.Blocked)
    elif dict['variable'] == 0 and current_state == tello_state.Blocked:
        switch_state(tello_state.Hovering)

    # Check for person detection
    persons = dict.get('persons', [])
    if persons and current_state not in [tello_state.Landed, tello_state.PersonFound]:
        switch_state(tello_state.PersonFound)
        print(f"Person detected: {persons}")
        person_found_last_print_time = time.time()
    elif current_state == tello_state.PersonFound:
        current_time = time.time()
        if current_time - person_found_last_print_time >= 2:
            print(f"Person detected: {persons}")
            person_found_last_print_time = current_time
    elif not persons and current_state == tello_state.PersonFound:
        switch_state(tello_state.Hovering)

stop_event.set()
state_thread.join()
exit()
