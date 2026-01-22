from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('database',views.database,name='database'),
    path('attendance/',views.Attendance),
    path('detect/',views.start_detection,name='start_detect'),
    path('stop/',views.stop_detection,name='stop_detect'),
    path('train/',views.train_faces,name='start_train'),
    path('status/',views.detect_status,name='detect_status'),
    path('video/',views.vid,name='video_feed'),
    path('confirmation/',views.confirmation,name='confirmation'),
    path('manual-entry/',views.manual_entry,name='manual_entry'),
]
