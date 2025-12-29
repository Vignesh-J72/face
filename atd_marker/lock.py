import threading

detect_running=False
detect_locked=threading.Lock()

# Outputs

last_identity="none"
status='idle'
logs=[]
current_frame=None
confirm_needed=False
confirm_shown=False
confirm_name=None
confirm_given=False