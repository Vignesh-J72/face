import datetime
import cv2
from deepface import DeepFace 
import firebase_admin
from firebase_admin import db,credentials



DB_PATH = "dataset/"         
MODEL_NAME = "ArcFace"        
DETECTOR = "retinaface"           
THRESHOLD = 0.7               
deepface_interval=10
cred=credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred,{'databaseURL':'https://first-project-c1f7b-default-rtdb.asia-southeast1.firebasedatabase.app/'})
cur_date=datetime.datetime.now().strftime("%d-%m-%Y")
def add_attendance(name):
    print("name",name)
    reference_profile=db.reference('Attendance/'+name.lower())
    print(name.lower())
    result=reference_profile.get()
    print(result)
        
    if cur_date in result:
        print(f"Attendance has already been saved for today ({cur_date})")
        print("Would you like to log the clock out time? (y/n)")
        choice=input().lower()
        if choice=='y':
            reference_profile=db.reference('Attendance/'+name.lower()+'/'+cur_date)
            reference_profile.update({
                "Clocked out at":datetime.datetime.now().strftime("%H:%M:%S")
            })
            print(f"Clock out time logged for {name} at {datetime.datetime.now().strftime('%H:%M:%S')}")
            clock_in=datetime.datetime.strptime(db.reference('Attendance/'+name.lower()+'/'+cur_date+"/Clocked in at").get(),"%H:%M:%S")
            
            clock_out=datetime.datetime.strptime(db.reference('Attendance/'+name.lower()+'/'+cur_date+"/Clocked out at").get(),"%H:%M:%S")
            reference_profile.update({"Total time worked":f"{clock_out-clock_in}"})
        return
    reference_profile.update({cur_date:""})
    reference_profile=db.reference('Attendance/'+name.lower()+'/'+cur_date)
    reference_profile.update({"Status":"Present",
        "Clocked in at":datetime.datetime.now().strftime("%H:%M:%S")
    })
    print(f"Attendance marked for {name} on {cur_date}")
    
        

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
    if last_identity!="No Face" and last_identity!="Unknown" and last_identity!=None and last_identity!="none":
       print(f"identified:{last_identity} at {datetime.datetime.now().strftime('%H:%M:%S')}")
       add_attendance(last_identity)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

   
   
   
   
   
   
   
   
   
   
   
   


