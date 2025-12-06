import os
import firebase_admin
from firebase_admin import db,credentials


cred=credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred,{
'databaseURL':'https://first-project-c1f7b-default-rtdb.asia-southeast1.firebasedatabase.app/'})

path="Vasanth"
ref=db.reference('Users/'+path.lower())
print(ref.get())

