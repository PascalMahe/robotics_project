import socket
import time
import threading
import cv2
import numpy as np
import torch
import pickle
from filelock import FileLock

# Initialize YOLO model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')

# Initialize MiDaS model
midas = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
midas.to(device)
midas.eval()
transforms = torch.hub.load('intel-isl/MiDaS', 'transforms')
transform = transforms.small_transform

# Tello connection details
tello_IP = '192.168.10.1'
tello_port_cmd = 8889
host = '192.168.10.2'
host_port_cmd = 8891
host_port_state = 8890
host_port_video = 'udp://@0.0.0.0:11111'

# Setting up sockets
locaddr_cmd = (host, host_port_cmd)
sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address_cmd = (tello_IP, tello_port_cmd)
sock_cmd.bind(locaddr_cmd)

locaddr_state = (host, host_port_state)
sock_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_state.bind(locaddr_state)


def do_command(cmd):
    sock_cmd.sendto(cmd.encode(encoding="utf-8"),
                    tello_address_cmd)  # Send Tello
    data, server = sock_cmd.recvfrom(1518)  # Wait response
    resp = data.decode(encoding="utf-8")
    return resp.replace("\r\n", "")


def parse_state_data(data):
    state_dict = {}
    for item in data.split(';'):
        if ':' in item:
            key, value = item.split(':')
            state_dict[key] = value
    return state_dict


def receive_state(stop_event):
    last_read_time = time.time()
    while not stop_event.is_set():
        try:
            data, server = sock_state.recvfrom(1518)
            state_info = data.decode(encoding="utf-8")
            state_dict = parse_state_data(state_info)
            current_time = time.time()
            if current_time - last_read_time >= 5:  # prevent spam
                # print(f"State Information: \n {state_dict}")
                last_read_time = current_time
        except UnicodeDecodeError:
            print(f"Unicode decode error: {data}")
        except Exception as e:
            print(f"Error receiving state: {str(e)}")


# Dictionary handling
variable_dict = {}


def save_dict():
    with FileLock('variable_dict.pkl.lock'):
        with open('variable_dict.pkl', 'wb') as f:
            pickle.dump(variable_dict, f)


def load_dict():
    try:
        with FileLock('variable_dict.pkl.lock'):
            with open('variable_dict.pkl', 'rb') as f:
                return pickle.load(f)
    except FileNotFoundError:
        return {}


variable_dict['variable'] = 0
save_dict()


def is_close_to_wall(img, nb_th, value_th):
    size = img.shape[0] * img.shape[1]
    nb_pix_th = int(size * nb_th)
    count_close = np.sum(img > value_th) / size
    return count_close > nb_th


def receive_video(stop_event):
    cap = cv2.VideoCapture(host_port_video)
    if not cap.isOpened():
        print("Failed to open video stream")
        return
    print("Video stream opened successfully")
    count = 0
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            time.sleep(0.1)
            continue
        # YOLO Object Detection
        results = model(frame)
        for result in results.xyxy[0].cpu().numpy():
            x1, y1, x2, y2, conf, cls = result
            if conf > 0.35:
                tl = (int(x1), int(y1))
                br = (int(x2), int(y2))
                label = model.names[int(cls)]
                text = f'{label}: {conf:.2f}'
                frame = cv2.rectangle(frame, tl, br, (255, 0, 0), 2)
                frame = cv2.putText(
                    frame, text, (tl[0], tl[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # MiDaS Depth Estimation
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        count += 1
        if count == 24:
            imgbatch = transform(img).to(device)
            with torch.no_grad():
                prediction = midas(imgbatch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode='bicubic',
                    align_corners=False
                ).squeeze()
                depth_map = prediction.cpu().numpy()
                depth_map = (depth_map - depth_map.min()) / \
                    (depth_map.max() - depth_map.min())
                too_close = is_close_to_wall(depth_map, 0.4, 0.5)
                variable_dict['variable'] = int(too_close)
                save_dict()
            cv2.imshow('Depth', depth_map)
            count = 0

        cv2.imshow('Tello Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


# Start the video and state threads
stop_event = threading.Event()
video_thread = threading.Thread(target=receive_video, args=(stop_event,))
video_thread.start()
state_thread = threading.Thread(target=receive_state, args=(stop_event,))
state_thread.start()

# Command sequence
print(f"Sending 'command': {do_command('command')}")
print(f"Sending 'streamon': {do_command('streamon')}")

try:
    print(f"Sending 'takeoff': {do_command('takeoff')}")
    time.sleep(5)
    # print(f"Sending 'up 100': {do_command('up 100')}")
    # time.sleep(5)
    print(f"Sending 'ccw 360': {do_command('ccw 360')}")
    time.sleep(5)
    print(f"Sending 'land': {do_command('land')}")
finally:
    print(f"Sending 'streamoff': {do_command('streamoff')}")
    stop_event.set()
    state_thread.join()
    video_thread.join()
    sock_cmd.close()
