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


midas = torch.hub.load('intel-isl/MiDaS','MiDaS_small')
device = 'cuda'
midas.to(device)
midas.eval()

transforms = torch.hub.load('intel-isl/MiDaS','transforms')
transform = transforms.small_transform


# Initialize the variable and the dictionary
variable_value = 0
variable_dict = {}

# Save the dictionary to a file
def save_dict():
    with FileLock('variable_dict.pkl.lock'):
        with open('variable_dict.pkl', 'wb') as f:
            pickle.dump(variable_dict, f)

# Load the dictionary from a file
def load_dict():
    try:
        with FileLock('variable_dict.pkl.lock'):
            with open('variable_dict.pkl', 'rb') as f:
                return pickle.load(f)
    except FileNotFoundError:
        return {}


tello_IP = '192.168.10.1'
tello_port_cmd = 8889

host = '192.168.10.2'
host_port_cmd = 8891
# Not used currently (have speed / accel / height ect...)
host_port_video = 'udp://@0.0.0.0:11111'


variable_dict['variable'] = 0
save_dict()





#retour = do_command("command")
#print(f"Retour de 'command': {retour}")
#etat_batterie = do_command("battery?")
#print(f"Retour de 'battery?': {etat_batterie}")

#model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')
movecount =0

def is_close_to_wall(img,nb_th,value_th):
    size = img.shape[0]*img.shape[1]
    nb_pix_th = int(size*nb_th)
    # Get number of pixels that have a value superior to value th
    count_close = np.sum(img>value_th)/size
    
    return count_close > nb_th


def receive_video(stop_event):
    global movecount
    global current_state
    global speeds
    # Receive video stream from the Tello drone
    # NB: cv2.VideoCapture handle on its own socket creation ect...
    cap = cv2.VideoCapture(host_port_video)

    if not cap.isOpened():
        print("Failed to open video stream")
        return
    waiting_to_turn = False
    print("Video stream opened successfully")
    count = 0
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            time.sleep(0.1)
            continue
        count+=1
        img = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        if(count == 24):
            imgbatch = transform(img).to(device)

            with torch.no_grad():
                prediction = midas(imgbatch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size = img.shape[:2],
                    mode='bicubic',
                    align_corners=False
                ).squeeze()
                depth_map = prediction.cpu().numpy()
                depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())

                too_close = is_close_to_wall(depth_map,0.4,0.5)

                variable_dict['variable'] = int(too_close)
                save_dict()

                
                
            cv2.imshow('Depth',depth_map)
            count=0


        




        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Q WAS PRESSED")
            break

        cv2.imshow('CV2Frame',frame)

    cap.release()
    cv2.destroyAllWindows()
    stop_event.set()
    video_thread.join()
    exit()




# Start the video thread
stop_event = threading.Event()
video_thread = threading.Thread(target=receive_video, args=(stop_event,))
video_thread.start()

# Start state thread

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
