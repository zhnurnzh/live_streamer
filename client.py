import cv2
import tkinter as tk
from PIL import Image, ImageTk
import torch
import numpy as np
import sys
import os

# Add YOLOv5 repo path (adjust this if needed)
yolo_path = os.path.join(os.getcwd(), 'yolov5')
if yolo_path not in sys.path:
    sys.path.append(yolo_path)

# Load the YOLOv5 model (default 'yolov5s')
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
model.conf = 0.5  # Confidence threshold
model.classes = [0]  # Only detect 'person' class

is_paused = False
detection_enabled = False  # New toggle flag
cap = None
frame = None

def start_stream():
    global cap, is_paused
    is_paused = False
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        update_frame()

def stop_stream():
    global cap, is_paused
    is_paused = True
    if cap and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()

def toggle_detection():
    global detection_enabled
    detection_enabled = not detection_enabled
    status = "ON" if detection_enabled else "OFF"
    toggle_btn.config(text=f"Detection: {status}")

def update_frame():
    global cap, frame, is_paused

    if cap and cap.isOpened() and not is_paused:
        ret, frame = cap.read()
        if ret:
            frame_flipped = cv2.flip(frame, 1)
            frame_resized = cv2.resize(frame_flipped, (640, 480))

            if detection_enabled:
                # Convert to RGB for model
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

                # Run YOLOv5 inference
                results = model(frame_rgb)
                detections = results.xyxy[0].cpu().numpy()

                # Draw bounding boxes
                for *xyxy, conf, cls in detections:
                    label = f"{results.names[int(cls)]} {conf:.2f}"
                    x1, y1, x2, y2 = map(int, xyxy)
                    cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame_resized, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Convert to RGB for Tkinter display
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            canvas.imgtk = imgtk

    if not is_paused:
        root.after(33, update_frame)

# Create the GUI
root = tk.Tk()
root.title("Camera Stream Controller with YOLOv5")

canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

start_btn = tk.Button(root, text="Play", command=start_stream, width=15)
start_btn.pack(pady=10)

stop_btn = tk.Button(root, text="Stop", command=stop_stream, width=15)
stop_btn.pack(pady=10)

toggle_btn = tk.Button(root, text="Detection: OFF", command=toggle_detection, width=15)
toggle_btn.pack(pady=10)

root.mainloop()
# records and captures 