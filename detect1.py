import datetime
import cv2
from deepface import DeepFace 

DB_PATH = "dataset/"         
MODEL_NAME = "ArcFace"        
DETECTOR = "retinaface"           
THRESHOLD = 0.7               
deepface_interval=10

cap = cv2.VideoCapture(0)
cap.set(3, 640)  
cap.set(4, 480) 
frame_count=0
last_identity="none"

print("Starting webcam...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    frame_count += 1
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    ).detectMultiScale(gray, 1.3, 5)
    if len(faces)>0:
        (x,y,w,h)=faces[0]
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        if frame_count % deepface_interval==0:
            try:
                res=DeepFace.find(
                    img_path=frame,
                    db_path=DB_PATH,
                    model_name=MODEL_NAME,
                    detector_backend=DETECTOR,
                    enforce_detection=False)
                if res and len(res[0])>0:
                    row=res[0].iloc[0]
                    identity_path=row["identity"].replace("\\","/")
                    distance=row["distance"]
                    print(row)
                    if distance<THRESHOLD:
                        last_identity=identity_path.split("/")[-2]
                    else:
                        last_identity="Unknown"
            except:
                last_identity="Unknown"
    else:
        last_identity="No Face"
    cv2.putText(frame, last_identity, (30,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
    cv2.imshow("Face Scanner", frame)
    if last_identity!="No Face" or last_identity!="Unknown":
        print(f"Identified: {last_identity} at {datetime.datetime.now()}")
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
    
   
   
   
   
   
   
   
   
   
   
   
   



'''try:
        result = DeepFace.find(
            img_path=frame,
            db_path=DB_PATH,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR,
            enforce_detection=False
        )
    except Exception as e:
        print("Error:", e)
        continue

    person = "No Face"

    if result and len(result[0]) > 0:

        row = result[0].iloc[0]
        identity_path = row["identity"].replace("\\", "/")
        distance = row["distance"]

        if distance < THRESHOLD:
            person = identity_path.split("/")[-2]
        else:
            person = "Unknown"

    cv2.putText(frame, person, (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Face Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()'''
