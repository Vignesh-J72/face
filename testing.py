import os
import firebase_admin
from firebase_admin import db,credentials
import datetime

cred=credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred,{
'databaseURL':'https://first-project-c1f7b-default-rtdb.asia-southeast1.firebasedatabase.app/'})

path="Vasanth"
name="Vasanth"
ref=db.reference('Users/'+path.lower())
print(ref.get())
cur_date=datetime.datetime.now().strftime("%d-%m-%Y")
print(db.reference('Attendance/'+path.lower()).get())
clock_in=db.reference('Attendance/'+name.lower()+'/'+cur_date+"/Clocked in at").get()
           
clock_out=db.reference('Attendance/'+name.lower()+'/'+cur_date+"/Clocked out at").get()
print(clock_out)