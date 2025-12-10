import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from deepface import DeepFace
import cv2
import datetime
import threading
import queue
import time

database = "dataset/"
model = "ArcFace"
detector = "opencv"

frame_queue = queue.Queue(maxsize=1)
result_queue = queue.Queue(maxsize=1)
stop_thread = False

def process_face_recognition():
    global stop_thread
    while not stop_thread:
        try:
            frame = frame_queue.get(timeout=0.1)
            try:
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                
                result = DeepFace.find(img_path=small_frame, db_path=database, model_name=model, detector_backend=detector,
                                     enforce_detection=False, silent=True)
                if not result_queue.empty():
                    try:
                        result_queue.get_nowait()
                    except queue.Empty:
                        pass
                result_queue.put(result)
            except Exception as e:
                print(f"Error in recognition: {e}")
                pass
        except queue.Empty:
            continue

recognition_thread = threading.Thread(target=process_face_recognition)
recognition_thread.daemon = True
recognition_thread.start()

print("Starting camera...")

cap = cv2.VideoCapture(0)
current_result = None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if frame_queue.empty():
        try:
            frame_queue.put_nowait(frame.copy()) 
        except queue.Full:
            pass

    if not result_queue.empty():
        try:
            current_result = result_queue.get_nowait()
        except queue.Empty:
            pass
            
    if current_result is None:
        cv2.putText(frame, "Scanning...", (25, 25), cv2.FONT_ITALIC, 1, (255, 255, 0), 2)
    elif len(current_result) > 0:
        try:
            df = current_result[0]
            if not df.empty:
                name = df.iloc[0]['identity']
                person = name.split("/")[-2]
                distance = df.iloc[0]['distance'] if 'distance' in df.columns else 0.0

                x = int(df.iloc[0]['source_x']) * 2
                y = int(df.iloc[0]['source_y']) * 2
                w = int(df.iloc[0]['source_w']) * 2
                h = int(df.iloc[0]['source_h']) * 2

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                cv2.putText(frame, "Matched", (x, y - 40), cv2.FONT_ITALIC, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, f"Name: {person}", (x, y - 20), cv2.FONT_ITALIC, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Unknown", (50, 50), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
        except Exception as e:
            pass

    cv2.imshow("Live face:", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        stop_thread = True
        break

cap.release()
cv2.destroyAllWindows()
recognition_thread.join(timeout=1.0)

