import datetime,time
import cv2
from deepface import DeepFace 
import firebase_admin
from firebase_admin import db,credentials
import os
from atd_marker import lock

def add_attendance(name):
    cur_date=datetime.datetime.now().strftime("%d-%m-%Y")
    print("name",name)
    reference_profile=db.reference('Attendance/'+name.lower())
    print(name.lower())
    result=reference_profile.get()
    print(result)
        
    if cur_date in result:
        lock.logs.append(f"Attendance has already been saved for today ({cur_date})")
        lock.logs.append("Would you like to log the clock out time? (y/n)")
        lock.confirm_needed=True
        lock.confirm_name=name
        lock.confirm_given=None
        while lock.confirm_given is None:
            time.sleep(0.1)
        

        
        if lock.confirm_given is True:
            reference_profile=db.reference('Attendance/'+name.lower()+'/'+cur_date)
            reference_profile.update({
                "Clocked out at":datetime.datetime.now().strftime("%H:%M:%S")
            })
            lock.logs.append(f"Clock out time logged for {name} at {datetime.datetime.now().strftime('%H:%M:%S')}")
            clock_in=datetime.datetime.strptime(db.reference('Attendance/'+name.lower()+'/'+cur_date+"/Clocked in at").get(),"%H:%M:%S")
            
            clock_out=datetime.datetime.strptime(db.reference('Attendance/'+name.lower()+'/'+cur_date+"/Clocked out at").get(),"%H:%M:%S")
            reference_profile.update({"Total time worked":f"{clock_out-clock_in}"})
        elif lock.confirm_given is False:
            lock.logs.append("Clock out not logged.")
        lock.confirm_needed=False
        lock.confirm_name=None
        lock.confirm_given=False
        return
    reference_profile.update({cur_date:""})
    reference_profile=db.reference('Attendance/'+name.lower()+'/'+cur_date)
    reference_profile.update({"Status":"Present",
        "Clocked in at":datetime.datetime.now().strftime("%H:%M:%S")
    })
    lock.logs.append(f"Attendance marked for {name} on {cur_date}")
    
def start_detect():
    lock.status='running'
    base_directory=os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(base_directory, "dataset/")
    MODEL_NAME = "ArcFace"        
    DETECTOR = "retinaface"           
    THRESHOLD = 0.7               
    deepface_interval=10
    key=os.path.join(base_directory,"firebase_key.json")
    cred=credentials.Certificate(key)
    firebase_admin.initialize_app(cred,{'databaseURL':'https://first-project-c1f7b-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    cur_date=datetime.datetime.now().strftime("%d-%m-%Y")
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  
    cap.set(4, 480) 
    frame_count=0
    lock.last_identity="none"
    
    print("Starting webcam...")
    while True:
        with lock.detect_locked:
            if not lock.detect_running:
                break   
        ret, frame = cap.read()
        if not ret:
          continue
        frame_count += 1
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml").detectMultiScale(gray, 1.3, 5)
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
                            lock.last_identity=identity_path.split("/")[-2]
                        else:
                            lock.last_identity="Unknown"
                except:
                    lock.last_identity="Unknown"
        else:
         lock.last_identity="No Face"
        cv2.putText(frame, lock.last_identity, (30,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
        lock.current_frame=frame.copy()
        if lock.last_identity!="No Face" and lock.last_identity!="Unknown" and lock.last_identity!=None and lock.last_identity!="none":
            print(f"identified:{lock.last_identity} at {datetime.datetime.now().strftime('%H:%M:%S')}")
            lock.logs.append(f"{lock.last_identity} at {datetime.datetime.now().strftime('%H:%M:%S')}")
            add_attendance(lock.last_identity)
            if len(lock.logs)>=15:
                lock.logs.pop(0)
    cap.release()
    lock.status='idle'


if __name__ == "__main__":
    start_detect()
   
   
   
   

   
   
   
   
   
   
   
   


