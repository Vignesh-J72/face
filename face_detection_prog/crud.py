import firebase_admin
from firebase_admin import db,credentials
import os


def create_data():
    print("1. Create new profile and database")
    print("2. Add data to existing profile")
    create_choice= input("Enter your choice: ")
    if create_choice=='1':
        path=input("Enter profile name: ")
        if path not in os.listdir("dataset/"):
            os.mkdir("dataset/"+path)
        if path not in db.reference('Users/').get():    
            ref=db.reference('Users/'+path)
            ref.child(path).set(True)
            attn_ref=db.reference('Attendance/'+path)
            attn_ref.child(path).set(True)
        print("Profile created successfully.")
    elif create_choice=='2':
        path=input("Enter profile name:")
        if path in os.listdir("dataset/"):
           profile_res=read_data(path)
           print(profile_res)
           ref1=db.reference('Users/'+path)
           user_data=ref1.get()
           while True:
               print("Available data:", user_data)
               user_choice=input("Enter the key to add data:")
               user_value=input("Enter the value:")
               ref1.update({user_choice:user_value})
               print("Data added successfully")
               choice=input("Do you want to add more data? (y/n): ")
               if choice.lower()!='y':
                   break
    return

def read_data(profile_name=None):
    if profile_name==None:
        ref=db.reference('Users/')
        print(ref.get())
        attn=db.reference('Attendance/')
        print(attn.get())
        return 
    else:
        ref=db.reference('Users/'+profile_name)
        print(ref.get())
        attn=db.reference('Attendance/'+profile_name)
        print(attn.get())
    return

def update_data():
    path=input("Enter profile name to update data: ").lower()
    choice=input("1. Update user data\n2. Update attendance data\nEnter your choice:(1/2)")
    res1=db.reference('Users/')
    res11=res1.get()
    print(res11)
    if path not in res11:
        print("Profile does not exist.")
        return
    if choice=='1':
        ref=db.reference('Users/'+path)
        key=input("Enter the key to update:")
        value=input("Enter the new value:")
        ref.update({
            key:value
        })
        print("Data updated successfully.")
    elif choice=='2':
        ref=db.reference('Attendance/'+path)
        date=input("Enter date to update attendance (DD-MM-YYYY):")
        status=input("Enter new status (Present/Absent):")
        ref=db.reference('Attendance/'+path+'/'+date)
        ref.update({"Status":status})
        print("Attendance updated successfully.")
    return

def delete_data():
    path=input("Enter profile name to delete data: ")
    choice=input("1. Delete user data\n2. Delete attendance data\nEnter your choice:(1/2)")
    res1=db.reference('Users/'+path)
    res11=res1.get()
    print(res11)
    if choice=='1':
        ref=db.reference('Users/'+path)
        print(ref.get())
        choice=input("Enter the key to delete:")
        ref1=ref.child(choice)
        ref1.delete()
        print("User data deleted successfully.")
    elif choice=='2':
        ref=db.reference('Attendance/'+path)
        choice=input("Enter date to delete attendance (DD-MM-YYYY):")
        ref1=ref.child(choice)
        ref1.delete()
        print("Attendance data deleted successfully.")
    return

def menu():
    cred=credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred,{
    'databaseURL':'https://first-project-c1f7b-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    while True:
        print("1. Create Data")
        print("2. Read Data")
        print("3. Update Data")
        print("4. Delete Data")
        print("5. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            create_data()
        elif choice == '2':
            Username=input("Enter profile name to read data (leave blank to read all):").lower()
            read_data(Username)
        elif choice == '3':
            update_data()
        elif choice == '4':
            delete_data()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.") 
        
if __name__ == "__main__":
    menu()