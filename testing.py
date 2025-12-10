import requests

#low level rest api
url='https://first-project-c1f7b-default-rtdb.asia-southeast1.firebasedatabase.app/Attendance.json?auth=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'
ans=requests.get(url).json()
for i in ans:
    print(i,ans[i])