from django.shortcuts import render
from django.http import JsonResponse
from threading import Thread
from django.http import HttpResponse
import json,os
from face_detection_prog.detect import start_detect
from face_detection_prog.train1 import start_train
from face_detection_prog.crud import menu
import threading
from . import lock
import cv2
from django.http import StreamingHttpResponse
from atd_marker import lock
import time
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import db,credentials
import firebase,firebase_admin

detect_thread=None


def home(request):
    return render(request,'home.html')

def Attendance(request):
   base_directory=os.path.dirname(os.path.abspath(__file__))
   key=os.path.join(base_directory,"firebase_key.json")
   cred=credentials.Certificate(key)

   try:
       firebase_admin.initialize_app(cred,{'databaseURL':'https://first-project-c1f7b-default-rtdb.asia-southeast1.firebasedatabase.app/'})
   except ValueError:
       pass
   
   ref=db.reference('Attendance/')
   result=ref.get()
   
   attendance_list = []
   seen = set()

   if result:
    for name, dates in result.items():
        if not isinstance(dates, dict):
            continue

        for date, details in dates.items():
            key = (name, date)
            if key in seen:
                continue
            seen.add(key)

            row = {
                'name': name,
                'date': date
            }

            if isinstance(details, dict):
                row.update(details)

            attendance_list.append(row)



   
   return JsonResponse(attendance_list, safe=False)
def start_detection(request):
  global detect_thread
  
  with lock.detect_locked:
    if not lock.detect_running:
        lock.detect_running = True
        detect_thread = threading.Thread(target=start_detect, daemon=True)
        detect_thread.start()

    return HttpResponse("Detection started")


def stop_detection(request):
    lock.detect_running = False
    return HttpResponse("Detection stopped")


def train_faces(request):
    threading.Thread(target=start_train, daemon=True).start()
    lock.logs.append("training started")
    return HttpResponse("Training started")

def detect_status(request):
   return JsonResponse({
       'status': lock.status,
       'logs':lock.logs,
       'last_identity':lock.last_identity,
       'running':lock.detect_running,
       'confirm_needed':lock.confirm_needed,
       'confirm_name':lock.confirm_name})

def vid(request):
   def gen():
      while True:
         frame=lock.current_frame
         if frame is None:
            time.sleep(0.05)
            continue
         ret,jpeg=cv2.imencode('.jpg',frame)
         if not ret:
            continue
         yield(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+bytearray(jpeg)+b'\r\n\r\n')
         time.sleep(0.030)
   return StreamingHttpResponse(gen(),content_type='multipart/x-mixed-replace; boundary=frame')



def confirmation(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    data = json.loads(request.body)
    lock.confirm_given = data.get("response")
    print(data.get("response"))
    

    return JsonResponse({"ok": True})


def database(request):
   return render(request,'database.html')

def manual_entry(request):
    if request.method != "POST":
         return JsonResponse({"success": False, "error": "POST only"}, status=400)
    
    try:
       data=json.loads(request.body)
       record={
          "name":data['name'],
          "date":data['date'],
          "status":data['Status'],
          "clock_in":data.get("Clocked in at",""),
          "clock_out":data.get("Clocked out at",""),
          "total_time":data.get("Total time worked","")
       }
       db.reference(f'Attendance/{record["name"].lower()}/{record["date"]}').update({
          "Status":record["status"],
          "Clocked in at":record["clock_in"],
          "Clocked out at":record["clock_out"],
          "Total time worked":record["total_time"]
    

       })
       return JsonResponse({"success": True})
    except Exception as e:
       return JsonResponse({"success": False, "error": str(e)}, status=500)
       