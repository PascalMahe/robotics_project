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


variable_dict = load_dict()


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

        # Reduce resolution for faster processing
        frame = cv2.resize(frame, (640, 480))

        # Process every nth frame for YOLO
        if count % 3 == 0:
            # YOLO Object Detection
            results = model(frame)
            persons = []
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
                    if label == 'person':
                        persons.append((tl, br, conf))

            variable_dict['persons'] = persons

        # Process every nth frame for MiDaS
        if count % 6 == 0:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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

        count += 1
        cv2.imshow('Tello Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Start the video thread
stop_event = threading.Event()
video_thread = threading.Thread(target=receive_video, args=(stop_event,))
video_thread.start()
