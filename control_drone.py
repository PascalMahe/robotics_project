import socket
import time
import threading
import cv2
import numpy as np
#import torch
from sklearn.cluster import DBSCAN
from transformers import pipeline
import cv2
from PIL import Image
import requests
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
import torch
from enum import Enum
import keyboard  
import pickle
from filelock import FileLock

class tello_state(Enum):
    Landed = 0,
    Moving = 1,
    Hovering = 2,
    Blocked =3,


current_state = tello_state.Landed

tello_IP = '192.168.10.1'
tello_port_cmd = 8889

host = '192.168.10.2'
host_port_cmd = 8891
# Not used currently (have speed / accel / height ect...)
host_port_state = 8890
#host_port_video = 'udp://@0.0.0.0:11111'

# Connecting local host to tello with socket
locaddr_cmd = (host, host_port_cmd)
sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address_cmd = (tello_IP, tello_port_cmd)
sock_cmd.bind(locaddr_cmd)

locaddr_state = (host, host_port_state)
sock_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_state.bind(locaddr_state)

def load_dict():
    try:
        with FileLock('variable_dict.pkl.lock'):
            with open('variable_dict.pkl', 'rb') as f:
                return pickle.load(f)
    except FileNotFoundError:
        return {}


def do_command(cmd):
    sock_cmd.sendto(cmd.encode(encoding="utf-8"),
                    tello_address_cmd)  # Send Tello
    data, server = sock_cmd.recvfrom(1518)  # Wait response

    resp = data.decode(encoding="latin-1")
    return resp.replace("\r\n", "")

def switch_state(new_state:tello_state):
    global current_state
    print("Switching from",current_state," to",new_state)
    current_state = new_state

def parse_state_data(data):
    state_dict = {}
    for item in data.split(';'):
        if ':' in item:
            key, value = item.split(':')
            state_dict[key] = value
    return state_dict
current_xspeed = 0
speeds = [0,0,0]
def receive_state(stop_event):
    global speeds
    last_read_time = time.time()
    while not stop_event.is_set():
        try:
            data, server = sock_state.recvfrom(1518)
            state_info = data.decode(encoding="utf-8")
            state_dict = parse_state_data(state_info)
            current_time = time.time()
            if current_time - last_read_time >= 2:  # prevent spam
                print(f"State Information: \n {state_dict}")
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

#model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')
movecount =0

def is_close_to_wall(img,nb_th,value_th):
    size = img.shape[0]*img.shape[1]
    nb_pix_th = int(size*nb_th)
    # Get number of pixels that have a value superior to value th
    count_close = np.sum(img>value_th)/size
    
    return count_close > nb_th




# Start the video thread
stop_event = threading.Event()

# Start state thread
state_thread = threading.Thread(target=receive_state, args=(stop_event,))
state_thread.start()
print(f"Sending 'streamon': {do_command('streamon')}")

while(True):


    if(current_state == tello_state.Hovering):
        print(f"Sending 'forward': {do_command('forward 30')}")
        switch_state(tello_state.Moving)
        time.sleep(1)

        movecount+=1
    elif(current_state == tello_state.Blocked):
            # Set waiting to turn to avoid turning before having the image analysed again
            print(f"Sending 'cw': {do_command('cw 45')}")
            ######################################
            #####"# Faire un sleep  de 2 secs pour forcer à attendre que ce soit fait et qu'on analyse la nouvelle image
            time.sleep(2)


    elif(current_state == tello_state.Moving and speeds == [0,0,0]):
                
        switch_state(tello_state.Hovering)


    if(keyboard.is_pressed('e')):
        if(current_state == tello_state.Landed):
            print(f"Sending 'takeoff': {do_command('takeoff')}")
            switch_state(tello_state.Moving)

    if(keyboard.is_pressed('y')):
        print(f"Sending 'land': {do_command('land')}")
        break

    # Check too close
    dict = load_dict()
    
    if(dict['variable'] == 1 and current_state != tello_state.Landed and current_state != tello_state.Blocked):
        switch_state(tello_state.Blocked)
    elif(dict['variable'] == 0 and current_state == tello_state.Blocked):
        switch_state(tello_state.Hovering)



        #if(current_state == tello_state.Hovering):
        #    print(f"Sending 'forward': {do_command('forward 20')}")
        #    switch_state(tello_state.Moving)
        #    movecount+=1
        #elif(current_state == tello_state.Blocked):
        #    if(not waiting_to_turn):
        #        # Set waiting to turn to avoid turning before having the image analysed again
        #        waiting_to_turn = True
        #        print(f"Sending 'cw': {do_command('cw 20')}")

stop_event.set()
state_thread.join()
exit()





## Command sequence
#print(f"Sending 'command': {do_command('command')}")

# Take off
#print(f"Sending 'takeoff': {do_command('takeoff')}")

#
#try:
#    print(f"Sending 'takeoff': {do_command('takeoff')}")
#    time.sleep(5)
#    print(f"Sending 'up 100': {do_command('up 100')}")
#    time.sleep(5)
#    print(f"Sending 'ccw 360': {do_command('ccw 360')}")
#    time.sleep(5)
#    print(f"Sending 'land': {do_command('land')}")
#finally:
#    print(f"Sending 'streamoff': {do_command('streamoff')}")
#    stop_event.set()
#    state_thread.join()
#    video_thread.join()
#    sock_cmd.close()
